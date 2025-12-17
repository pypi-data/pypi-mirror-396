"""
History and conversation state handlers.

Handles undo, clear, get_history, and get_cost operations.
"""

import sys
import io
from fastapi import WebSocket
from app.state import AppState
from orchestral.ui.web.render import render_message_to_html, render_agent_panel_to_html
from orchestral.llm.base.response import Response
from orchestral.context.message import Message
from orchestral.ui.format_context import _pair_tool_calls_with_responses


async def handle_undo(websocket: WebSocket, data: dict, state: AppState, get_model_info_func):
    """
    Handle undo last user message.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
        get_model_info_func: Function to get current model info
    """
    success = state.agent.context.undo()
    if success:
        # Save updated context
        if state.current_conversation_id:
            state.conversation_manager.save_conversation(
                state.agent.context,
                conversation_id=state.current_conversation_id,
                model_info=get_model_info_func(),
                tools=state.agent.llm.tools,
                base_directory=state.initial_base_directory
            )
        await websocket.send_json({
            "type": "info",
            "message": "Undone"
        })
    else:
        await websocket.send_json({
            "type": "error",
            "message": "Nothing to undo"
        })


async def handle_clear(websocket: WebSocket, data: dict, state: AppState, get_model_info_func):
    """
    Handle clear conversation.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
        get_model_info_func: Function to get current model info
    """
    # Clear conversation messages
    state.agent.context.clear(preserve_system_prompt=True)

    # Reset conversation state to start fresh
    state.current_conversation_id = None
    state.auto_name_generated = False

    await websocket.send_json({
        "type": "info",
        "message": "Conversation cleared"
    })


async def handle_get_history(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle get conversation history request.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    # Suppress terminal output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        agent_content_buffer = []  # Buffer agent responses between user messages
        agent_buffer_start_index = None  # Track the index for TeX/edit functionality
        agent_with_tools_index = None  # Track the first assistant message with tool_calls

        async def flush_agent_buffer(agent_message_index=None):
            """Send buffered agent content as a single panel."""
            nonlocal agent_buffer_start_index, agent_with_tools_index  # Need this to modify the outer variables

            if agent_content_buffer:
                content_items = []
                model_name = None

                # Process each agent response in the buffer
                for response in agent_content_buffer:
                    # Get model name from first response if show_model_names is enabled
                    if model_name is None and state.show_model_names:
                        model_name = response.model

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
                            state.agent.context
                        )
                        for tool_use in tool_uses:
                            content_items.append({
                                'type': 'tool',
                                'name': tool_use['name'],
                                'arguments': tool_use['arguments'],
                                'output': tool_use['output'],
                                'is_failed': tool_use.get('is_failed', False)
                            })

                # Send agent panel with all content
                if content_items:
                    # Use the index of the first assistant with tool_calls if available,
                    # otherwise use the first assistant message in the buffer
                    message_idx = agent_with_tools_index if agent_with_tools_index is not None else agent_buffer_start_index

                    html = render_agent_panel_to_html(content_items, 100, model_name=model_name)
                    await websocket.send_json({
                        "type": "agent_update",
                        "content": html,
                        "message_index": message_idx  # Include index for TeX/edit functionality
                    })

                agent_content_buffer.clear()
                # Reset the buffer indices
                agent_buffer_start_index = None
                agent_with_tools_index = None

        # Process messages in order (same logic as format_context)
        for i, item in enumerate(state.agent.context.messages):
            if isinstance(item, Message):
                if item.role == 'user':
                    # Flush buffered agent content before user message
                    await flush_agent_buffer(agent_buffer_start_index)

                    # Send user message with index for edit functionality
                    html = render_message_to_html(item.role, item.text or "(no content)", 100)
                    await websocket.send_json({
                        "type": "user_message",
                        "content": html,
                        "message_index": i  # Include index for edit feature
                    })

                elif item.role == 'system':
                    # Only show system prompt if toggle is enabled
                    if state.show_system_prompt:
                        # Flush buffered agent content before system message
                        await flush_agent_buffer(agent_buffer_start_index)

                        # Send system message
                        html = render_message_to_html(item.role, item.text or "(no content)", 100)
                        await websocket.send_json({
                            "type": "user_message",
                            "content": html,
                            "message_index": i  # Include index for TeX/edit functionality
                        })

                elif item.role == 'tool':
                    # Tool response - will be paired with tool calls
                    continue

            elif isinstance(item, Response):
                # Track the index of the first assistant message in this buffer
                if agent_buffer_start_index is None:
                    agent_buffer_start_index = i

                # Track the first assistant message with tool_calls (important for TeX conversion)
                if agent_with_tools_index is None and item.message.tool_calls:
                    agent_with_tools_index = i

                # Buffer agent responses to group them
                agent_content_buffer.append(item)

        # Flush any remaining agent content at the end
        await flush_agent_buffer(agent_buffer_start_index)

    finally:
        sys.stdout = old_stdout


async def handle_get_cost(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle get cost request.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    try:
        cost = state.agent.get_total_cost()
        print(f"[App] Cost requested: ${cost:.4f}")
        await websocket.send_json({
            "type": "cost_info",
            "cost": cost
        })
    except Exception as e:
        print(f"[App] Cost error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to get cost: {str(e)}"
        })
