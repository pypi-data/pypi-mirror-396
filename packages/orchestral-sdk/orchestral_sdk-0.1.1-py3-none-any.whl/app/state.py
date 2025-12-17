"""
Application State Management

Encapsulates all global application state in a single dataclass.
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class AppState:
    """
    Encapsulates all application state for the Orchestral web server.

    This replaces the module-level global variables in server.py with a single
    state object that can be easily passed to functions and tested.

    Attributes:
        agent: The configured Agent instance with LLM and tools
        agent_handler: WebSocket handler for agent interactions
        conversation_manager: Manages conversation persistence
        current_conversation_id: ID of the currently active conversation
        auto_name_generated: Whether AI name generation has occurred for current conversation
        non_streaming_models: Set of model names that don't support streaming
        show_model_names: Whether to display model names in agent panels
        streaming_enabled: Whether streaming mode is enabled globally
        show_system_prompt: Whether to display system prompts in conversations
        initial_tools: List of tools configured at startup
        initial_base_directory: Base directory for file operations
        approval_callback: Callback function for UserApprovalHook to request user approval
        enabled_tools: Dict mapping tool class names to enabled state (True/False)
    """
    agent: Optional['Agent'] = None
    agent_handler: Optional['WebSocketAgentHandler'] = None
    conversation_manager: Optional['ConversationManager'] = None
    current_conversation_id: Optional[str] = None
    auto_name_generated: bool = False
    non_streaming_models: set = field(default_factory=set)
    show_model_names: bool = False
    streaming_enabled: bool = True
    show_system_prompt: bool = False
    initial_tools: Optional[list] = None
    initial_base_directory: Optional[str] = None
    approval_callback: Optional[callable] = None
    enabled_tools: dict = field(default_factory=dict)
