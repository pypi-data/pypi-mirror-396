"""
Approval Bridge - Bridges synchronous hook callbacks with async WebSocket communication.

This module provides the mechanism for UserApprovalHook to request user approval
through the WebSocket while remaining synchronous.
"""

import asyncio
import threading
from typing import Optional, Callable


class ApprovalDisconnectException(Exception):
    """Raised when an approval is denied due to WebSocket disconnect."""
    pass


class ApprovalBridge:
    """
    Manages the communication between synchronous hooks and async WebSocket.

    The hook (running in the agent's thread) blocks waiting for approval,
    while the WebSocket handler (in the async event loop) sends/receives messages.
    """

    def __init__(self):
        self.pending_approval: Optional[asyncio.Future] = None
        self.pending_data: Optional[dict] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.websocket_send: Optional[Callable] = None

    def set_websocket(self, websocket_send: Callable, event_loop: asyncio.AbstractEventLoop):
        """
        Set the WebSocket send function and event loop.

        Args:
            websocket_send: Async function to send messages to WebSocket
            event_loop: The asyncio event loop running the WebSocket
        """
        self.websocket_send = websocket_send
        self.event_loop = event_loop

    def request_approval(self, tool_name: str, arguments: dict, description: str) -> bool:
        """
        Request user approval (BLOCKING).

        This is called from the synchronous hook and blocks until the user responds.

        Args:
            tool_name: Name of the tool requesting approval
            arguments: Tool arguments
            description: Human-readable description of the action

        Returns:
            True if approved, False if denied
        """
        if not self.websocket_send or not self.event_loop:
            raise RuntimeError("ApprovalBridge not initialized with WebSocket")

        # Check if we're already in the event loop's thread
        try:
            # Try to get the running loop
            asyncio.get_running_loop()

            # We're in the event loop - need to use a different approach
            import threading

            # Create a threading event to signal completion
            result_container = {'approved': False}
            completion_event = threading.Event()

            async def run_and_signal():
                result = await self._async_request_approval(tool_name, arguments, description)
                result_container['approved'] = result
                completion_event.set()

            # Schedule the coroutine
            asyncio.ensure_future(run_and_signal())

            # Block this thread until completion
            completion_event.wait()

            return result_container['approved']

        except RuntimeError:
            # Not in an event loop - use run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(
                self._async_request_approval(tool_name, arguments, description),
                self.event_loop
            )
            return future.result()

    async def _async_request_approval(self, tool_name: str, arguments: dict, description: str) -> bool:
        """
        Async implementation of approval request.

        Sends message to frontend and waits for response.
        """
        # Create a Future to hold the user's response
        self.pending_approval = asyncio.Future()
        self.pending_data = {
            'tool_name': tool_name,
            'arguments': arguments,
            'description': description
        }

        # Send approval request to frontend
        await self.websocket_send({
            "type": "approval_request",
            "tool_name": tool_name,
            "arguments": arguments,
            "description": description
        })

        # Wait for user response (this will be resolved by handle_approval_response)
        approved = await self.pending_approval

        # Clean up
        self.pending_approval = None
        self.pending_data = None

        return approved

    async def handle_approval_response(self, approved: bool, reason: str = None):
        """
        Handle the user's approval response from the frontend.

        Args:
            approved: True if user approved, False if denied
            reason: Optional reason for denial (e.g., "disconnect")
        """
        if self.pending_approval and not self.pending_approval.done():
            if not approved and reason == "disconnect":
                # Signal disconnect-based denial with exception
                self.pending_approval.set_exception(ApprovalDisconnectException("WebSocket disconnected"))
            else:
                self.pending_approval.set_result(approved)
        else:
            print("[ApprovalBridge] Warning: Received approval response with no pending request")

    def cancel_pending(self):
        """Cancel any pending approval request."""
        if self.pending_approval and not self.pending_approval.done():
            self.pending_approval.set_result(False)
            self.pending_approval = None
            self.pending_data = None

    def get_pending_approval_data(self) -> Optional[dict]:
        """
        Get the current pending approval data if any.

        Returns:
            Dict with tool_name, arguments, and description if approval is pending,
            None otherwise
        """
        if self.pending_approval and not self.pending_approval.done():
            return self.pending_data
        return None
