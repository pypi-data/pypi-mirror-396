"""
Base types and utilities for message handlers.

This module defines the common interface for all message handlers.
"""

from typing import Callable, Awaitable
from fastapi import WebSocket

# Type alias for message handler functions
# Each handler receives: websocket, message data dict, and app state
MessageHandler = Callable[[WebSocket, dict, 'AppState'], Awaitable[None]]
