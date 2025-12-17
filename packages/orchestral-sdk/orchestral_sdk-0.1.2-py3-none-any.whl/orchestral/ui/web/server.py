# NOTE: This is the OLD server.py and is not currently being used. I'm marking it for deprecation.

"""
FastAPI Server for Orchestral Web UI

Provides WebSocket interface for streaming agent interactions.
Runs locally, serves static files, handles real-time communication.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from orchestral.agent.agent import Agent
from orchestral.ui.web.agent_handler import WebSocketAgentHandler


# Create FastAPI app
app = FastAPI(title="Orchestral Web UI", version="0.1.0")

# Global agent instance (single-user local mode)
_agent: Optional[Agent] = None
_agent_handler: Optional[WebSocketAgentHandler] = None

# Global settings (using lists for mutability across references)
_streaming_enabled = [True]  # Default: streaming ON
_cache_enabled = [True]      # Default: caching ON


def set_agent(agent: Agent):
    """
    Set the agent instance for the web UI.

    Args:
        agent: Configured Agent instance with tools
    """
    global _agent, _agent_handler
    _agent = agent

    # Remove any display hooks (we don't want terminal output in web mode)
    agent.display_hook = None

    _agent_handler = WebSocketAgentHandler(
        agent,
        width=100,
        streaming_enabled_ref=_streaming_enabled,
        cache_enabled_ref=_cache_enabled
    )


# Serve static files (CSS, JS)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def get_index():
    """Serve the main HTML page."""
    index_path = STATIC_DIR / "index.html"

    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Orchestral Web UI</h1><p>Static files not found. Run from orchestral_core directory.</p>",
            status_code=500
        )

    return FileResponse(index_path)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for agent communication.

    Protocol:
    - Client sends: {"type": "chat", "message": "user message"}
    - Client sends: {"type": "interrupt"}
    - Server sends: {"type": "user_message", "content": "html"}
    - Server sends: {"type": "agent_update", "content": "html"}
    - Server sends: {"type": "interrupted", "message": "..."}
    - Server sends: {"type": "complete"}
    - Server sends: {"type": "error", "message": "..."}
    """
    if _agent is None or _agent_handler is None:
        await websocket.close(code=1011, reason="Agent not initialized")
        return

    await websocket.accept()

    # Track the current message handling task
    current_task = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            print(f"[Web UI] Received message: {data}")

            message_type = data.get("type")

            if message_type == "chat":
                # Handle chat message
                user_message = data.get("message", "")
                if user_message.strip():
                    print(f"[Web UI] User: {user_message[:50]}{'...' if len(user_message) > 50 else ''}")
                    # Run as background task so we can receive interrupts
                    current_task = asyncio.create_task(_agent_handler.handle_message(websocket, user_message))

            elif message_type == "interrupt":
                # Handle interrupt request
                print(f"[Web UI] Interrupt requested")
                _agent_handler.interrupt()
                # Don't send additional status message - client already shows it

            elif message_type == "clear":
                # Clear conversation
                _agent.context.clear(preserve_system_prompt=True)
                await websocket.send_json({
                    "type": "info",
                    "message": "Conversation cleared"
                })

            elif message_type == "get_history":
                # Send conversation history using same logic as format_context
                from orchestral.ui.web.render import render_message_to_html, render_agent_panel_to_html
                from orchestral.llm.base.response import Response
                from orchestral.context.message import Message
                from orchestral.ui.format_context import _pair_tool_calls_with_responses
                import sys
                import io

                # Suppress terminal output
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()

                try:
                    agent_content_buffer = []  # Buffer agent responses between user messages

                    async def flush_agent_buffer():
                        """Send buffered agent content as a single panel."""
                        if agent_content_buffer:
                            content_items = []

                            # Process each agent response in the buffer
                            for response in agent_content_buffer:
                                # Add response text if present
                                if response.message.text and response.message.text.strip():
                                    content_items.append({
                                        'type': 'text',
                                        'content': response.message.text
                                    })

                                # Add tool calls with their responses
                                if response.message.tool_calls:
                                    tool_uses = _pair_tool_calls_with_responses(
                                        response.message.tool_calls,
                                        _agent.context
                                    )
                                    for tool_use in tool_uses:
                                        content_items.append({
                                            'type': 'tool',
                                            'name': tool_use['name'],
                                            'arguments': tool_use['arguments'],
                                            'output': tool_use['output']
                                        })

                            # Send agent panel with all content
                            if content_items:
                                html = render_agent_panel_to_html(content_items, 100)
                                await websocket.send_json({
                                    "type": "agent_update",
                                    "content": html
                                })

                            agent_content_buffer.clear()

                    # Process messages in order (same logic as format_context)
                    for item in _agent.context.messages:
                        if isinstance(item, Message):
                            if item.role in ['user', 'system']:
                                # Flush buffered agent content before user/system message
                                await flush_agent_buffer()

                                # Send user/system message
                                html = render_message_to_html(item.role, item.text or "(no content)", 100)
                                await websocket.send_json({
                                    "type": "user_message",
                                    "content": html
                                })

                            elif item.role == 'tool':
                                # Tool response - will be paired with tool calls
                                continue

                        elif isinstance(item, Response):
                            # Buffer agent responses to group them
                            agent_content_buffer.append(item)

                    # Flush any remaining agent content at the end
                    await flush_agent_buffer()

                finally:
                    sys.stdout = old_stdout

            elif message_type == "toggle_streaming":
                # Toggle streaming mode
                enabled = data.get("enabled", True)
                _streaming_enabled[0] = enabled
                print(f"[Web UI] Streaming {'enabled' if enabled else 'disabled'}")

            elif message_type == "toggle_cache":
                # Toggle prompt caching
                enabled = data.get("enabled", True)
                _cache_enabled[0] = enabled
                print(f"[Web UI] Prompt caching {'enabled' if enabled else 'disabled'}")

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        # Client disconnected
        pass

    except Exception as e:
        # Unexpected error
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass  # Connection already closed


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "agent_initialized": _agent is not None
    }


@app.get("/api/theme")
async def get_theme():
    """Get theme configuration for frontend."""
    from orchestral.ui.colors import CODE_THEME, get_code_theme_background
    return {
        "code_theme": CODE_THEME,
        "code_background_color": get_code_theme_background()
    }


@app.get("/api/latex/orchestral-tex")
async def get_orchestral_tex():
    """Return the orchestral.tex LaTeX module content as JSON."""
    try:
        from orchestral.ui.latex.orchestral_tex_content import ORCHESTRAL_TEX_CONTENT
        return {"content": ORCHESTRAL_TEX_CONTENT}
    except Exception as e:
        return {"error": f"Error loading orchestral.tex: {str(e)}"}


def run_server(agent: Agent, host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    """
    Run the web UI server.

    Args:
        agent: Configured Agent instance
        host: Host to bind to (default: localhost)
        port: Port to bind to (default: 8000)
        open_browser: Whether to auto-open browser
    """
    import uvicorn

    # Set the agent
    set_agent(agent)

    # Open browser if requested
    if open_browser:
        import webbrowser
        import threading

        def open_browser_delayed():
            import time
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    # Run server
    print(f"\n🌐 Orchestral Web UI starting at http://{host}:{port}")
    print("Press Ctrl+C to stop\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="warning"  # Reduce noise
    )


if __name__ == "__main__":
    print("Orchestral Web UI Server")
    print("\nUsage:")
    print("  from orchestral import Agent")
    print("  from orchestral.ui.web import run_server")
    print("")
    print("  agent = Agent(tools=[...])")
    print("  run_server(agent)")
