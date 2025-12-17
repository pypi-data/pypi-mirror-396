"""
WebSocket Agent Handler

Handles agent interactions over WebSocket with interrupt support.
Bridges synchronous agent code with asynchronous WebSocket communication.

The agent now has built-in interrupt support, so this handler just needs to:
1. Set the interrupt flag on the agent
2. Run agent methods in threads
3. Forward chunks/updates to WebSocket
"""

import asyncio
import io
import os
import queue
import sys
import threading
from typing import Optional

from fastapi import WebSocket

from orchestral.agent.agent import Agent
from orchestral.llm.base.response import Response
from orchestral.ui.web.render import (
    render_message_to_html,
    render_agent_panel_to_html,
)
from orchestral.ui.format_context import _pair_tool_calls_with_responses


class WebSocketAgentHandler:
    """
    Handles WebSocket communication with an agent.

    Features:
    - Streams agent responses as HTML
    - Supports interrupts (Esc key) during streaming and tool execution
    - Agent handles interrupt logic internally
    - Bridges sync agent code with async WebSocket
    """

    def _get_agent_message_index(self) -> int:
        """
        Get the index where the current agent message is stored.

        Check if the last message in context is an assistant message.
        If yes, return its index (len - 1).
        If no, return the next index where it will be added (len).
        """
        if hasattr(self.agent.context, 'messages'):
            messages = self.agent.context.messages

            if messages:
                last_item = messages[-1]

                # Handle both Response and Message objects
                if hasattr(last_item, 'message'):
                    # It's a Response object
                    if last_item.message.role == 'assistant':
                        return len(messages) - 1
                elif hasattr(last_item, 'role'):
                    # It's a Message object
                    if last_item.role == 'assistant':
                        return len(messages) - 1

            # Otherwise, the assistant message will be added at the next index
            return len(messages)
        return -1

    def __init__(self, agent: Agent, width: int = 80, non_streaming_models: Optional[set] = None, show_model_names_ref: Optional[list] = None, streaming_enabled_ref: Optional[list] = None, cache_enabled_ref: Optional[list] = None):
        """
        Initialize handler.

        Args:
            agent: The agent instance
            width: Display width for rendering
            non_streaming_models: Set of model names that don't support streaming (optional)
            show_model_names_ref: Reference to global show_model_names flag (single-item list for mutability)
            streaming_enabled_ref: Reference to global streaming_enabled flag (single-item list for mutability)
            cache_enabled_ref: Reference to global cache_enabled flag (single-item list for mutability)
        """
        self.agent = agent
        self.width = width
        self.non_streaming_models = non_streaming_models if non_streaming_models is not None else set()
        self.show_model_names_ref = show_model_names_ref or [False]
        self.streaming_enabled_ref = streaming_enabled_ref or [True]
        self.cache_enabled_ref = cache_enabled_ref or [True]

        # Interrupt control - shared with agent
        self.should_stop = threading.Event()
        self.agent.interrupt_flag = self.should_stop

        # Tool streaming support
        self.tool_outputs = {}  # {tool_call_id: {'name': str, 'output': str, 'complete': bool}}
        self.current_websocket = None
        self.event_loop = None
        self.streaming_monitor_task = None
        self.tool_execution_active = False

        # Set tool streaming callback on agent
        self.agent.tool_stream_callback = self._on_tool_stream

        # Set tool completion callback on agent
        self.agent.tool_complete_callback = self._on_tool_complete

        # Cost tracking for threshold detection
        self.max_cost = None  # Maximum cost threshold (defaults to None)
        self.last_cost = 0.0  # Track last known cost for threshold detection
        self.cost_exceeded_interrupted = False  # Track if we've already interrupted for exceeding cost

    def _get_context_window(self) -> int:
        """Get the context window size for the current model."""
        model_name = self.agent.llm.model
        provider = self.agent.llm.__class__.__name__.lower()

        try:
            if 'claude' in provider or 'anthropic' in provider:
                from orchestral.llm.anthropic.model_details import get_context_window
                return get_context_window(model_name)
            elif 'gpt' in provider or 'openai' in provider:
                from orchestral.llm.openai.model_details import get_context_window
                return get_context_window(model_name)
            elif 'gemini' in provider or 'google' in provider:
                from orchestral.llm.google.model_details import get_context_window
                return get_context_window(model_name)
            elif 'groq' in provider:
                from orchestral.llm.groq.model_details import get_context_window
                return get_context_window(model_name)
            else:
                return 128000  # Default fallback
        except Exception:
            return 128000  # Default fallback on any error

    async def _send_usage_update(self, websocket: WebSocket):
        """Send current cost, token usage, context window, and max cost to frontend."""
        current_cost = self.agent.get_total_cost()

        # Check if cost threshold exceeded and interrupt if needed
        if self.max_cost is not None and not self.cost_exceeded_interrupted:
            if current_cost > self.max_cost and self.last_cost <= self.max_cost:
                # Cost just exceeded threshold - interrupt once
                self.should_stop.set()
                self.cost_exceeded_interrupted = True
                await websocket.send_json({
                    "type": "popup_notification",
                    "title": "Execution Interrupted",
                    "message": f"Cost exceeded limit of ${self.max_cost:.2f} (current: ${current_cost:.4f})",
                    "notification_type": "error"
                })

        self.last_cost = current_cost

        await websocket.send_json({
            "type": "usage_update",
            "cost": current_cost,
            "tokens": self.agent.get_total_tokens(),
            "context_window": self._get_context_window(),
            "max_cost": self.max_cost
        })

    async def handle_message(self, websocket: WebSocket, user_message: str):
        """
        Handle a user message - stream response and execute tools.

        Args:
            websocket: WebSocket connection
            user_message: User's message
        """
        self.should_stop.clear()
        was_interrupted = False  # Track if this specific message was interrupted

        # Store websocket and event loop for tool streaming callbacks
        self.current_websocket = websocket
        self.event_loop = asyncio.get_event_loop()
        self.tool_outputs.clear()  # Clear previous tool outputs

        # Send user message HTML (suppress terminal output)
        import sys
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            user_html = render_message_to_html("user", user_message, self.width)
        finally:
            sys.stdout = old_stdout

        # Get the index where the user message will be added
        # (it will be added when agent.run() or agent.stream_text_message() is called)
        user_message_index = len(self.agent.context.messages)

        await websocket.send_json({
            "type": "user_message",
            "content": user_html,
            "message_index": user_message_index  # Index where message will be added
        })

        # Check if streaming is disabled globally or if current model doesn't support it
        current_model = self.agent.llm.model
        if not self.streaming_enabled_ref[0] or current_model in self.non_streaming_models:
            # Use non-streaming mode
            await self._run_non_streaming(websocket, user_message)
            await websocket.send_json({"type": "complete"})
            return

        # Try to stream agent response, fallback to non-streaming if it fails
        streaming_succeeded = await self._stream_agent_response(websocket, user_message)

        # If streaming failed, retry with non-streaming mode
        if not streaming_succeeded:
            await self._run_non_streaming(websocket, user_message)
            await websocket.send_json({"type": "complete"})
            return

        # Check if interrupted after streaming
        if self.should_stop.is_set():
            was_interrupted = True
            await websocket.send_json({"type": "complete"})
            return

        # Handle tool execution loop if needed
        await self._handle_tool_loop(websocket)

        # Check if interrupted at ANY point - this must be checked BEFORE sending any final updates
        # to prevent race conditions with fast models like Groq
        if self.should_stop.is_set():
            was_interrupted = True

        # Only send final update if we weren't interrupted
        # This is the last update that consolidates everything
        if not was_interrupted:
            content_items = self._build_current_content_items()
            model_name = self._get_model_name_from_last_response() if self.show_model_names_ref[0] else None
            html = render_agent_panel_to_html(content_items, self.width, model_name=model_name)
            await websocket.send_json({
                "type": "agent_update",
                "content": html,
                "message_index": self._get_agent_message_index()
            })

        # Send completion signal
        await websocket.send_json({"type": "complete"})

    async def _stream_agent_response(self, websocket: WebSocket, user_message: str) -> bool:
        """
        Stream the agent's text response.

        The agent checks interrupt_flag internally and handles cleanup.

        Args:
            websocket: WebSocket connection
            user_message: User's message

        Returns:
            True if streaming succeeded, False if it failed and needs fallback
        """
        chunk_queue = queue.Queue()

        def run_streaming():
            """Run agent streaming in thread."""
            try:
                # Get cache setting
                use_cache = self.cache_enabled_ref[0]

                # Agent handles interrupt checking internally
                stream_generator = self.agent.stream_text_message(user_message, use_prompt_cache=use_cache)

                for text_chunk in stream_generator:
                    chunk_queue.put(("chunk", text_chunk))

                # Streaming complete
                chunk_queue.put(("done", None))

            except Exception as e:
                # Put the full exception object for analysis
                chunk_queue.put(("error", e))

        # Send chunks as they arrive
        accumulated_text = ""
        interrupted = False

        # Start agent thread AFTER setting up consumer state
        agent_thread = threading.Thread(target=run_streaming, daemon=True)
        agent_thread.start()

        while True:
            # Check if interrupted FIRST before processing any chunks
            if self.should_stop.is_set() and not interrupted:
                interrupted = True
                # print(f"[DEBUG] Interrupt detected in handler, stopping chunk display")
                # The agent checks interrupt_flag and handles cleanup internally
                # Just stop displaying chunks and wait for agent thread to finish

            # Get next chunk (blocking in executor to not block event loop)
            # No timeout - ensures all chunks are consumed in order
            try:
                msg_type, data = await asyncio.get_event_loop().run_in_executor(
                    None, chunk_queue.get
                )
            except Exception as e:
                # Unexpected error reading from queue
                await websocket.send_json({
                    "type": "error",
                    "message": f"Queue error: {str(e)}"
                })
                break

            if msg_type == "chunk":
                # Accumulate text (even if interrupted, for context consistency)
                accumulated_text += data

                # Only send updates if not interrupted
                # Check AGAIN right before sending to handle interrupt during chunk processing
                if not interrupted and not self.should_stop.is_set():
                    # Render with accumulated text (not from context yet - streaming not complete)
                    from orchestral.ui.web.render import render_agent_text_to_html
                    model_name = self.agent.llm.model if self.show_model_names_ref[0] else None
                    html = render_agent_text_to_html(accumulated_text, self.width, model_name=model_name)
                    await websocket.send_json({
                        "type": "agent_update",
                        "content": html,
                        "message_index": self._get_agent_message_index()
                    })
                elif interrupted:
                    # Silently drain chunks after interrupt
                    pass

            elif msg_type == "interrupted":
                # Agent finished draining after interrupt
                break

            elif msg_type == "error":
                # Check if this is a streaming-not-supported error
                error = data
                error_str = str(error)

                # Detect API errors that indicate streaming isn't supported
                # This is general and works for any provider
                is_streaming_error = (
                    "stream" in error_str.lower() or
                    "streaming" in error_str.lower() or
                    ("400" in error_str and "unsupported" in error_str.lower())
                )

                if is_streaming_error:
                    # Add model to non-streaming list
                    current_model = self.agent.llm.model
                    self.non_streaming_models.add(current_model)

                    # Notify user
                    await websocket.send_json({
                        "type": "info",
                        "message": f"Model {current_model} doesn't support streaming. Retrying without streaming..."
                    })

                    # Clear the context - the failed attempt added the user message but no response
                    # We need to remove the user message since _run_non_streaming will add it again
                    if self.agent.context.messages and self.agent.context.messages[-1].role == 'user':
                        self.agent.context.messages.pop()

                    # Return False to indicate streaming failed
                    return False
                else:
                    # Some other error - report it
                    await websocket.send_json({
                        "type": "error",
                        "message": error_str
                    })
                    return False

            elif msg_type == "done":
                break

        # Wait for thread to complete
        await asyncio.get_event_loop().run_in_executor(
            None, agent_thread.join, 5.0
        )

        # Send usage update after streaming completes (Response with usage is now in context)
        await self._send_usage_update(websocket)

        return True  # Streaming succeeded

    async def _monitor_tool_streaming(self):
        """
        Background task that monitors tool_outputs and sends updates.
        Runs independently of executor to avoid event loop blocking.
        """
        last_outputs_hash = None

        while self.tool_execution_active:
            # Check if context has changed (tool results added)
            # This detects when tools complete, even if they don't stream
            context_state = (
                len(self.agent.context.messages),
                # Hash the last message content to detect tool result additions
                hash(str(self.agent.context.messages[-1])) if self.agent.context.messages else 0
            )

            # Also check streaming output changes
            current_outputs_str = str([
                (k, v['name'], v['complete'], len(v['output']), v['output'][:100])
                for k, v in self.tool_outputs.items()
            ])

            current_hash = hash((context_state, current_outputs_str))

            if current_hash != last_outputs_hash:
                # Context or streaming outputs changed - send update
                await self._send_agent_panel_update()
                last_outputs_hash = current_hash

            # Check frequently to be responsive
            await asyncio.sleep(0.1)

    async def _handle_tool_loop(self, websocket: WebSocket, max_iterations: int = 10):
        """
        Handle multi-turn tool execution loop using agent's built-in methods.
        Follows the same pattern as the terminal UI.

        Args:
            websocket: WebSocket connection
            max_iterations: Maximum number of tool execution rounds
        """
        iteration = 0

        while iteration < max_iterations:
            if self.should_stop.is_set():
                break

            # Check if last response has tool calls
            last_response = self.agent.context.messages[-1]

            if not isinstance(last_response, Response) or not last_response.message.tool_calls:
                # No more tool calls
                break

            # Show tools in pending state (before execution)
            content_items = self._build_current_content_items()
            model_name = self._get_model_name_from_last_response() if self.show_model_names_ref[0] else None
            html = render_agent_panel_to_html(content_items, self.width, model_name=model_name)
            await websocket.send_json({
                "type": "agent_update",
                "content": html,
                "message_index": self._get_agent_message_index()
            })

            # Start streaming monitor task BEFORE tool execution
            self.tool_execution_active = True
            self.streaming_monitor_task = asyncio.create_task(self._monitor_tool_streaming())

            # Execute tool calls using agent's built-in method
            # Individual tool errors are handled by the agent itself (see agent.py:_handle_tool_call)
            # We don't catch exceptions here - let them propagate so bugs are visible
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.agent._handle_tool_calls
                )
            finally:
                # Always clean up streaming monitor, even if execution fails
                self.tool_execution_active = False
                if self.streaming_monitor_task:
                    await self.streaming_monitor_task
                    self.streaming_monitor_task = None

            # Mark all tools as complete (now in context with final output)
            for tool_id in list(self.tool_outputs.keys()):
                self.tool_outputs[tool_id]['complete'] = True

            # Show completed tools (including any error messages from hooks)
            content_items = self._build_current_content_items()
            model_name = self._get_model_name_from_last_response() if self.show_model_names_ref[0] else None
            html = render_agent_panel_to_html(content_items, self.width, model_name=model_name)
            await websocket.send_json({
                "type": "agent_update",
                "content": html,
                "message_index": self._get_agent_message_index()
            })

            if self.should_stop.is_set():
                break

            # Stream next LLM response after tools using agent's built-in method
            await self._stream_after_tools(websocket)

            iteration += 1

        if iteration >= max_iterations:
            await websocket.send_json({
                "type": "warning",
                "message": f"Reached maximum tool iterations ({max_iterations})"
            })

    async def _stream_after_tools(self, websocket: WebSocket):
        """
        Stream agent response after tool execution.

        Args:
            websocket: WebSocket connection
        """
        chunk_queue = queue.Queue()

        def run_streaming():
            """Run agent streaming in thread."""
            try:
                # Agent handles interrupt checking internally
                stream_generator = self.agent._stream_response()

                for text_chunk in stream_generator:
                    chunk_queue.put(("chunk", text_chunk))

                chunk_queue.put(("done", None))

            except Exception as e:
                chunk_queue.put(("error", str(e)))

        agent_thread = threading.Thread(target=run_streaming, daemon=True)
        agent_thread.start()

        # Accumulate streaming text
        accumulated_text = ""
        interrupted = False

        # Send chunks as they arrive
        while True:
            # Check if interrupted
            if self.should_stop.is_set() and not interrupted:
                interrupted = True

            msg_type, data = await asyncio.get_event_loop().run_in_executor(
                None, chunk_queue.get
            )

            if msg_type == "chunk":
                # Accumulate streaming text
                accumulated_text += data

                # Only send updates if not interrupted
                if not interrupted and not self.should_stop.is_set():
                    # Build content items: completed tools + streaming text
                    content_items = self._build_current_content_items()

                    # Add streaming text as a separate item
                    if accumulated_text.strip():
                        content_items.append({
                            'type': 'text',
                            'content': accumulated_text
                        })

                    model_name = self._get_model_name_from_last_response() if self.show_model_names_ref[0] else None
                    html = render_agent_panel_to_html(content_items, self.width, model_name=model_name)
                    await websocket.send_json({
                        "type": "agent_update",
                        "content": html,
                        "message_index": self._get_agent_message_index()
                    })

            elif msg_type == "error":
                await websocket.send_json({
                    "type": "error",
                    "message": data
                })
                break

            elif msg_type == "done":
                break

        # Wait for thread
        await asyncio.get_event_loop().run_in_executor(
            None, agent_thread.join, 5.0
        )

        # Send usage update after streaming completes (Response with usage is now in context)
        await self._send_usage_update(websocket)

    def _build_current_content_items(self) -> list:
        """
        Build content items from current context (text + tools).
        Includes streaming tool outputs if available.

        Returns:
            List of content item dicts
        """
        content_items = []

        # Find last user message
        last_user_idx = -1
        for i in range(len(self.agent.context.messages) - 1, -1, -1):
            msg = self.agent.context.messages[i]
            if hasattr(msg, 'role') and msg.role == 'user':
                last_user_idx = i
                break

        # Collect all responses after last user message
        for i in range(last_user_idx + 1, len(self.agent.context.messages)):
            item = self.agent.context.messages[i]

            if isinstance(item, Response):
                # Add text if present
                if item.message.text and item.message.text.strip():
                    content_items.append({
                        'type': 'text',
                        'content': item.message.text
                    })

                # Add tools if present
                if item.message.tool_calls:
                    tool_uses = _pair_tool_calls_with_responses(
                        item.message.tool_calls,
                        self.agent.context
                    )
                    for tool_use in tool_uses:
                        # Check if we have streaming output for this tool
                        tool_call_id = tool_use.get('id')
                        is_streaming = False
                        if tool_call_id in self.tool_outputs and not self.tool_outputs[tool_call_id]['complete']:
                            # Use streaming output (not yet in context)
                            output = self.tool_outputs[tool_call_id]['output']
                            is_streaming = True
                        else:
                            # Use final output from context
                            output = tool_use['output']

                        content_items.append({
                            'type': 'tool',
                            'name': tool_use['name'],
                            'arguments': tool_use['arguments'],
                            'output': output,
                            'is_streaming': is_streaming,
                            'is_failed': tool_use.get('is_failed', False)
                        })

        return content_items

    async def _run_non_streaming(self, websocket: WebSocket, user_message: str):
        """
        Run agent in non-streaming mode (fallback when streaming fails).

        Args:
            websocket: WebSocket connection
            user_message: User's message
        """
        def run_agent():
            """Run agent.run() in thread."""
            try:
                # Get cache setting
                use_cache = self.cache_enabled_ref[0]

                return self.agent.run(user_message, use_prompt_cache=use_cache)
            except Exception as e:
                raise e

        # Run agent in executor
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, run_agent
            )

            # Build and send final response
            content_items = self._build_current_content_items()
            model_name = self._get_model_name_from_last_response() if self.show_model_names_ref[0] else None
            html = render_agent_panel_to_html(content_items, self.width, model_name=model_name)
            await websocket.send_json({
                "type": "agent_update",
                "content": html,
                "message_index": self._get_agent_message_index()
            })

            # Send usage update after non-streaming run completes
            await self._send_usage_update(websocket)

        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Agent error: {str(e)}"
            })

    def _get_model_name_from_last_response(self) -> Optional[str]:
        """
        Get the model name from the last Response in context.

        Returns:
            Model name if available, None otherwise
        """
        for msg in reversed(self.agent.context.messages):
            if isinstance(msg, Response):
                return msg.model
        return None

    def _on_tool_stream(self, tool_call_id: str, tool_name: str, chunk: str):
        """
        Called when tool yields output chunk (runs in sync agent thread).
        Just accumulates output - the monitor task will send updates.

        Args:
            tool_call_id: ID of the tool call
            tool_name: Name of the tool
            chunk: Chunk of output from the tool
        """
        print(f"[STREAM] {tool_name} chunk: {repr(chunk[:50])}")

        # Accumulate output
        if tool_call_id not in self.tool_outputs:
            self.tool_outputs[tool_call_id] = {
                'name': tool_name,
                'output': chunk,
                'complete': False
            }
        else:
            self.tool_outputs[tool_call_id]['output'] += chunk

        # Monitor task will detect the change and send update

    def _on_tool_complete(self, tool_call_id: str, tool_name: str):
        """
        Called when a tool completes execution (runs in sync agent thread).
        Marks the tool as complete so the monitor can update the UI.

        Args:
            tool_call_id: ID of the tool call
            tool_name: Name of the tool
        """
        print(f"[COMPLETE] {tool_name} finished (id: {tool_call_id})")

        # Mark tool as complete in tool_outputs
        if tool_call_id in self.tool_outputs:
            self.tool_outputs[tool_call_id]['complete'] = True
        else:
            # Tool didn't stream output, but still completed - create entry
            self.tool_outputs[tool_call_id] = {
                'name': tool_name,
                'output': '',
                'complete': True
            }

        # Monitor task will detect the completion and send update

    async def _send_agent_panel_update(self):
        """
        Re-render and send the complete agent panel with current state (async).
        This includes any streaming tool outputs in progress.
        """
        if self.current_websocket:
            # Build content items (includes streaming outputs)
            content_items = self._build_current_content_items()
            model_name = self._get_model_name_from_last_response() if self.show_model_names_ref[0] else None

            # Suppress terminal output during rendering
            import sys
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                html = render_agent_panel_to_html(content_items, self.width, model_name=model_name)
            finally:
                sys.stdout = old_stdout

            await self.current_websocket.send_json({
                "type": "agent_update",
                "content": html,
                "message_index": self._get_agent_message_index()
            })

    def interrupt(self):
        """
        Interrupt current operation.

        Sets the flag - agent handles the rest internally.
        """
        self.should_stop.set()


if __name__ == "__main__":
    print("WebSocketAgentHandler - bridges sync agent with async WebSocket")
    print("Features:")
    print("  - Streaming with HTML rendering")
    print("  - Interrupt support (agent handles internally)")
    print("  - Multi-turn tool loops")
