"""
Message Handlers for Orchestral App WebSocket Server

This package contains handlers for different types of WebSocket messages.
Each handler is a function that processes a specific message type.
"""

# Import all handlers for easy access
from app.handlers.chat import handle_chat, handle_interrupt
from app.handlers.history import handle_undo, handle_clear, handle_get_history, handle_get_cost
from app.handlers.conversation import (
    handle_list_conversations,
    handle_load_conversation,
    handle_save_conversation,
    handle_delete_conversation,
    handle_rename_conversation,
    handle_duplicate_conversation,
)
from app.handlers.settings import (
    handle_change_model,
    handle_toggle_model_names,
    handle_toggle_streaming,
    handle_toggle_cache,
    handle_toggle_system_prompt,
    handle_set_system_prompt,
    handle_get_system_prompt,
    handle_reset_streaming_blocklist,
    handle_update_base_directory,
    handle_get_ollama_models,
    handle_get_tools_info,
    handle_toggle_tool,
    handle_set_max_cost,
)
from app.handlers.approval import handle_approval_response, handle_get_pending_approval
from app.handlers.edit import handle_get_message_text, handle_truncate_context
from app.handlers.models import handle_get_available_models
from app.handlers.voice import handle_voice_transcribe

__all__ = [
    # Chat handlers
    "handle_chat",
    "handle_interrupt",
    # History handlers
    "handle_undo",
    "handle_clear",
    "handle_get_history",
    "handle_get_cost",
    # Conversation handlers
    "handle_list_conversations",
    "handle_load_conversation",
    "handle_save_conversation",
    "handle_delete_conversation",
    "handle_rename_conversation",
    "handle_duplicate_conversation",
    # Settings handlers
    "handle_change_model",
    "handle_toggle_model_names",
    "handle_toggle_streaming",
    "handle_toggle_cache",
    "handle_toggle_system_prompt",
    "handle_set_system_prompt",
    "handle_get_system_prompt",
    "handle_reset_streaming_blocklist",
    "handle_update_base_directory",
    "handle_get_ollama_models",
    "handle_get_tools_info",
    "handle_toggle_tool",
    "handle_set_max_cost",
    # Approval handlers
    "handle_approval_response",
    "handle_get_pending_approval",
    # Edit handlers
    "handle_get_message_text",
    "handle_truncate_context",
    # Models handlers
    "handle_get_available_models",
    # Voice handlers
    "handle_voice_transcribe",
]
