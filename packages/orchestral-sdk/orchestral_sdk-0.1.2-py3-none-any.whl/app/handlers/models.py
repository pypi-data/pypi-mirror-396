"""
Models handler - provides available models info to frontend.
"""

from fastapi import WebSocket
from app.state import AppState
from orchestral.llm import get_available_models


async def handle_get_available_models(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle request for available models.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state (unused)
    """
    try:
        models = get_available_models()
        await websocket.send_json({
            "type": "available_models",
            "models": models
        })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to get models: {str(e)}"
        })
