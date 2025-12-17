"""
User approval handlers.

Handles approval request responses from the frontend.
"""

from fastapi import WebSocket
from app.state import AppState


async def handle_approval_response(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle user's response to an approval request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'approved' (bool)
        state: Application state
    """
    approved = data.get("approved", False)

    # The approval_callback should have set up an approval bridge
    # We need to get the bridge to resolve the pending request
    if hasattr(state, '_approval_bridge'):
        await state._approval_bridge.handle_approval_response(approved)
    else:
        print("[App] Warning: Received approval response but no bridge found")


async def handle_get_pending_approval(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle request for pending approval state.

    Sends the pending approval data to the frontend if there is one.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    print("[App] Checking for pending approval...")
    if hasattr(state, '_approval_bridge'):
        pending = state._approval_bridge.get_pending_approval_data()
        print(f"[App] Pending approval data: {pending}")
        if pending:
            # Re-send the approval request
            print(f"[App] Re-sending approval request to frontend")
            await websocket.send_json({
                "type": "approval_request",
                **pending
            })
        else:
            print("[App] No pending approval found")
    else:
        print("[App] No approval bridge found")
    # If no pending approval, do nothing (client will remain unblocked)
