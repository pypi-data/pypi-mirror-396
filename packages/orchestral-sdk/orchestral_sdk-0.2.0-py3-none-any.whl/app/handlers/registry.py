"""
Message Handler Registry and Dispatcher.

Central registry of all message type handlers with validation and error handling.
"""

from typing import Dict, Callable, Awaitable
from fastapi import WebSocket
from app.state import AppState
from app.handlers import *


# Message handler signature that includes get_model_info_func for handlers that need it
MessageHandler = Callable[[WebSocket, dict, AppState], Awaitable[None]]
MessageHandlerWithModelInfo = Callable[[WebSocket, dict, AppState, Callable], Awaitable[None]]


# Registry of message type handlers
# Handlers are organized by category for clarity
MESSAGE_HANDLERS: Dict[str, tuple] = {
    # Chat operations
    "chat": (handle_chat, True),  # (handler, needs_model_info)
    "interrupt": (handle_interrupt, False),

    # History operations
    "undo": (handle_undo, True),
    "clear": (handle_clear, True),
    "get_history": (handle_get_history, False),
    "get_cost": (handle_get_cost, False),

    # Conversation management
    "list_conversations": (handle_list_conversations, False),
    "load_conversation": (handle_load_conversation, False),
    "save_conversation": (handle_save_conversation, True),
    "delete_conversation": (handle_delete_conversation, False),
    "rename_conversation": (handle_rename_conversation, False),
    "duplicate_conversation": (handle_duplicate_conversation, False),

    # Settings
    "change_model": (handle_change_model, False),
    "toggle_model_names": (handle_toggle_model_names, False),
    "toggle_streaming": (handle_toggle_streaming, False),
    "toggle_cache": (handle_toggle_cache, False),
    "toggle_system_prompt": (handle_toggle_system_prompt, False),
    "set_system_prompt": (handle_set_system_prompt, False),
    "get_system_prompt": (handle_get_system_prompt, False),
    "reset_streaming_blocklist": (handle_reset_streaming_blocklist, False),
    "update_base_directory": (handle_update_base_directory, False),
    "get_ollama_models": (handle_get_ollama_models, False),
    "get_available_models": (handle_get_available_models, False),
    "get_tools_info": (handle_get_tools_info, False),
    "toggle_tool": (handle_toggle_tool, False),
    "set_max_cost": (handle_set_max_cost, False),

    # Approval
    "approval_response": (handle_approval_response, False),
    "get_pending_approval": (handle_get_pending_approval, False),

    # Edit operations
    "get_message_text": (handle_get_message_text, False),
    "truncate_context": (handle_truncate_context, False),

    # Voice operations
    "voice_transcribe": (handle_voice_transcribe, False),
}


async def dispatch_message(
    message_type: str,
    websocket: WebSocket,
    data: dict,
    state: AppState,
    get_model_info_func: Callable
):
    """
    Dispatch message to appropriate handler with validation and error handling.

    Args:
        message_type: Type of message to handle
        websocket: WebSocket connection
        data: Message data
        state: Application state
        get_model_info_func: Function to get current model info

    Returns:
        Task object if handler returns one (e.g., chat handler), None otherwise
    """
    handler_info = MESSAGE_HANDLERS.get(message_type)

    if handler_info is None:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })
        return None

    handler, needs_model_info = handler_info

    try:
        # Call handler with or without model_info function based on its needs
        if needs_model_info:
            result = await handler(websocket, data, state, get_model_info_func)
        else:
            result = await handler(websocket, data, state)

        return result  # May be None or a Task object (from chat handler)

    except Exception as e:
        print(f"[Registry] Handler error for {message_type}: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send_json({
            "type": "error",
            "message": f"Handler error: {str(e)}"
        })
        # Re-raise for logging
        raise
