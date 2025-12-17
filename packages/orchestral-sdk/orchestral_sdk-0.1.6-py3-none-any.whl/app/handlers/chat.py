"""
Chat message handlers.

Handles chat messages and interrupts.
"""

import asyncio
from fastapi import WebSocket
from app.state import AppState
from app.services.conversation_service import auto_save_conversation, auto_generate_name


async def handle_chat(websocket: WebSocket, data: dict, state: AppState, get_model_info_func):
    """
    Handle chat message from user.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'message' field
        state: Application state
        get_model_info_func: Function to get current model info
    """
    user_message = data.get("message", "")
    if not user_message.strip():
        return

    print(f"[App] User: {user_message[:50]}{'...' if len(user_message) > 50 else ''}")

    # Fix any orphaned tool calls from previous interrupts before processing new message
    # This prevents API errors about tool_use blocks without tool_result blocks
    print(f"[App] Checking for orphaned tool calls before processing message...")
    state.agent.context.fix_tool_call_mismatches()
    print(f"[App] Context fixed. Message count: {len(state.agent.context.messages)}")

    # For new conversations, generate conversation_id BEFORE first message
    # This ensures tools can write to the correct location from the start
    if state.current_conversation_id is None:
        from app.services.conversation_service import update_tools_conversation_id
        # Generate timestamp-based ID
        conversation_id = state.conversation_manager._get_timestamp_id()
        state.current_conversation_id = conversation_id
        state.agent.conversation_id = conversation_id
        # Update all tools with the new conversation_id
        update_tools_conversation_id(state, conversation_id)
        print(f"[App] Generated conversation_id for new conversation: {conversation_id}")

    # Create auto-save callback that runs after task completes
    async def handle_and_save(ws, msg):
        # Run agent handler
        await state.agent_handler.handle_message(ws, msg)

        # Get model info for saving
        model_info = get_model_info_func()

        # Auto-save after agent completes
        state.current_conversation_id = auto_save_conversation(
            state,
            model_info,
            use_default_name=True
        )

        # Auto-generate name after first exchange
        print(f"[App] Auto-name check: auto_name_generated={state.auto_name_generated}, message_count={len(state.agent.context.messages)}")
        name = auto_generate_name(state, model_info)
        if name:
            print(f"[App] Auto-generated conversation name: {name}")

    # Run as background task so we can receive interrupts
    # Note: We return the task so the caller can track it
    return asyncio.create_task(handle_and_save(websocket, user_message))


async def handle_interrupt(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle interrupt request.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    print(f"[App] Interrupt requested")
    state.agent_handler.interrupt()
