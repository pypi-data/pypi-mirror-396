"""
Conversation service for auto-save and auto-naming logic.
"""

from typing import Optional
from app.state import AppState


def update_tools_conversation_id(state: AppState, conversation_id: str):
    """
    Update conversation_id on all tools that support it.

    Args:
        state: Application state
        conversation_id: Conversation ID to inject into tools
    """
    if not state.agent or not state.agent.llm or not state.agent.llm.tools:
        return

    from orchestral.tools.base.field_utils import is_state_field

    for tool in state.agent.llm.tools:
        # Check if tool has conversation_id field
        tool_class = tool.__class__
        if hasattr(tool_class, 'model_fields') and 'conversation_id' in tool_class.model_fields:
            field_info = tool_class.model_fields['conversation_id']
            if is_state_field(field_info):
                # Directly update the tool's conversation_id
                tool.conversation_id = conversation_id


def auto_save_conversation(
    state: AppState,
    model_info: Optional[dict],
    use_default_name: bool = False
) -> Optional[str]:
    """
    Auto-save the current conversation.

    Args:
        state: Application state
        model_info: Model provider and name
        use_default_name: If True and no name exists, use "New Conversation"

    Returns:
        Conversation ID, or None if save failed
    """
    if not state.conversation_manager or not state.agent:
        return None

    name = None
    if use_default_name and not state.auto_name_generated:
        name = "New Conversation"

    # Use actual loaded tools from the agent
    tools = state.agent.llm.tools if state.agent.llm else state.initial_tools

    # Preserve tools.json for existing conversations (don't overwrite)
    preserve_tools = state.current_conversation_id is not None

    conversation_id = state.conversation_manager.save_conversation(
        state.agent.context,
        conversation_id=state.current_conversation_id,
        name=name,
        model_info=model_info,
        tools=tools,
        base_directory=state.initial_base_directory,
        preserve_tools=preserve_tools
    )

    # Update agent's conversation_id and all tools
    if conversation_id:
        state.agent.conversation_id = conversation_id
        update_tools_conversation_id(state, conversation_id)

    return conversation_id


def auto_generate_name(state: AppState, model_info: Optional[dict]) -> Optional[str]:
    """
    Generate and save an AI-generated conversation name if appropriate.

    This should be called after the first user-agent exchange when there
    is enough context to generate a meaningful name.

    Args:
        state: Application state
        model_info: Model provider and name

    Returns:
        Generated name if successful, None otherwise
    """
    # Check if we should generate a name
    if state.auto_name_generated:
        return None

    if len(state.agent.context.messages) <= 2:
        return None

    if not state.conversation_manager or not state.current_conversation_id:
        return None

    try:
        # Generate name using AI
        name = state.conversation_manager.generate_conversation_name(state.agent.context)

        # Use actual loaded tools from the agent
        tools = state.agent.llm.tools if state.agent.llm else state.initial_tools

        # Save conversation with new name (preserve tools since this is an existing conversation)
        state.conversation_manager.save_conversation(
            state.agent.context,
            conversation_id=state.current_conversation_id,
            name=name,
            model_info=model_info,
            tools=tools,
            base_directory=state.initial_base_directory,
            preserve_tools=True  # Don't overwrite tools.json during auto-naming
        )

        # Mark as generated
        state.auto_name_generated = True

        return name

    except Exception as e:
        print(f"[App] Failed to generate name: {e}")
        return None
