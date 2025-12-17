"""
Service modules for business logic.

Services encapsulate reusable business logic that can be called
from multiple handlers.
"""

from .model_service import get_model_info
from .conversation_service import auto_save_conversation, auto_generate_name

__all__ = [
    'get_model_info',
    'auto_save_conversation',
    'auto_generate_name',
]
