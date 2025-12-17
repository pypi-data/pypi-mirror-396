"""
Edit message handlers.

Handles message editing and context truncation for edit & resend functionality.
"""

from fastapi import WebSocket
from app.state import AppState


async def handle_get_message_text(websocket: WebSocket, data: dict, state: AppState):
    """
    Get the text of a specific message for editing.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'message_index'
        state: Application state
    """
    message_index = data.get("message_index")

    if message_index is None:
        await websocket.send_json({
            "type": "error",
            "message": "Missing message_index"
        })
        return

    # Get message from context
    try:
        message = state.agent.context.messages[message_index]
        text = message.text or ""

        await websocket.send_json({
            "type": "message_text",
            "text": text
        })
    except IndexError:
        await websocket.send_json({
            "type": "error",
            "message": f"Message index {message_index} out of range"
        })


async def handle_truncate_context(websocket: WebSocket, data: dict, state: AppState):
    """
    Truncate context before a specific message index (for edit & resend).

    Args:
        websocket: WebSocket connection
        data: Message data containing 'message_index'
        state: Application state
    """
    message_index = data.get("message_index")

    if message_index is None:
        await websocket.send_json({
            "type": "error",
            "message": "Missing message_index"
        })
        return

    # Truncate context before the specified index
    try:
        original_count = len(state.agent.context.messages)
        state.agent.context.messages = state.agent.context.messages[:message_index]
        new_count = len(state.agent.context.messages)

        print(f"[Edit] Truncated context from {original_count} to {new_count} messages (before index {message_index})")

        # No message sent to frontend - silent truncation for seamless edit experience
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to truncate context: {str(e)}"
        })
