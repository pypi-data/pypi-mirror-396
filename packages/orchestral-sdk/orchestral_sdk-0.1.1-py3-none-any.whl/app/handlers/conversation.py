"""
Conversation management handlers.

Handles list, load, save, delete, rename, and duplicate operations.
"""

from fastapi import WebSocket
from app.state import AppState
from app.services.conversation_service import update_tools_conversation_id


async def handle_list_conversations(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle list conversations request.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    conversations = state.conversation_manager.list_conversations()
    await websocket.send_json({
        "type": "conversations_list",
        "conversations": conversations
    })


async def handle_load_conversation(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle load conversation request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'conversation_id'
        state: Application state
    """
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        await websocket.send_json({
            "type": "error",
            "message": "No conversation_id provided"
        })
        return

    try:
        # Load the conversation, passing available tools for introspection matching
        context, metadata, tools = state.conversation_manager.load_conversation(
            conversation_id,
            available_tools=state.initial_tools
        )

        # Update agent's conversation_id and context
        state.agent.conversation_id = conversation_id
        state.agent.context = context
        state.current_conversation_id = conversation_id
        state.auto_name_generated = True  # Name already exists

        # Load saved tools if available, otherwise use initial tools
        if tools is not None:
            loaded_tools = tools
            print(f"[App] Loaded {len(loaded_tools)} tools from conversation")
        else:
            loaded_tools = state.initial_tools
            print(f"[App] Using initial tools (no tools.json found)")

        # Reset enabled_tools state to match loaded conversation
        # This makes tool toggles per-conversation instead of global
        state.enabled_tools = {tool.__class__.__name__: True for tool in loaded_tools}

        # Switch to the saved model if available
        if "model" in metadata:
            model_info = metadata["model"]
            provider = model_info.get("provider")
            model = model_info.get("model")

            if provider and model:
                try:
                    # Import LLM classes
                    from orchestral.llm import Claude, GPT, Gemini

                    # Create new LLM instance
                    if provider == "anthropic":
                        new_llm = Claude(model=model)
                    elif provider == "openai":
                        new_llm = GPT(model=model)
                    elif provider == "google":
                        new_llm = Gemini(model=model)
                    else:
                        raise ValueError(f"Unknown provider: {provider}")

                    # Set loaded tools on new LLM
                    new_llm.set_tools(loaded_tools)
                    state.agent.llm = new_llm

                    print(f"[App] Switched to model: {provider}/{model}")

                    # Notify frontend about model change
                    await websocket.send_json({
                        "type": "model_changed",
                        "provider": provider,
                        "model": model
                    })

                except Exception as e:
                    print(f"[App] Failed to switch model: {e}")
        else:
            # No saved model, just update tools
            state.agent.llm.set_tools(loaded_tools)

        # Update conversation_id on all loaded tools
        update_tools_conversation_id(state, conversation_id)

        # Update base directory from loaded conversation
        loaded_base_directory = metadata.get("base_directory")
        if loaded_base_directory:
            state.initial_base_directory = loaded_base_directory
            # Notify frontend
            await websocket.send_json({
                "type": "base_directory_info",
                "base_directory": loaded_base_directory
            })

        # Send success message
        await websocket.send_json({
            "type": "info",
            "message": f"Loaded: {metadata.get('name', 'Unknown')}"
        })

        # Send usage update for the loaded conversation
        await websocket.send_json({
            "type": "usage_update",
            "cost": state.agent.get_total_cost(),
            "tokens": state.agent.get_total_tokens()
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to load conversation: {str(e)}"
        })


async def handle_save_conversation(websocket: WebSocket, data: dict, state: AppState, get_model_info_func):
    """
    Handle manual save conversation request.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
        get_model_info_func: Function to get current model info
    """
    try:
        state.current_conversation_id = state.conversation_manager.save_conversation(
            state.agent.context,
            conversation_id=state.current_conversation_id,
            model_info=get_model_info_func(),
            tools=state.agent.llm.tools,
            base_directory=state.initial_base_directory
        )
        await websocket.send_json({
            "type": "info",
            "message": "Conversation saved"
        })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to save: {str(e)}"
        })


async def handle_delete_conversation(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle delete conversation request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'conversation_id'
        state: Application state
    """
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        await websocket.send_json({
            "type": "error",
            "message": "No conversation_id provided"
        })
        return

    try:
        success = state.conversation_manager.delete_conversation(conversation_id)
        if success:
            # If we deleted the current conversation, reset
            if conversation_id == state.current_conversation_id:
                state.current_conversation_id = None
                state.auto_name_generated = False

            await websocket.send_json({
                "type": "info",
                "message": "Conversation deleted"
            })
            # Refresh conversation list
            conversations = state.conversation_manager.list_conversations()
            await websocket.send_json({
                "type": "conversations_list",
                "conversations": conversations
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": "Conversation not found"
            })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to delete: {str(e)}"
        })


async def handle_rename_conversation(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle rename conversation request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'conversation_id' and 'new_name'
        state: Application state
    """
    conversation_id = data.get("conversation_id")
    new_name = data.get("new_name")

    if not conversation_id or not new_name:
        await websocket.send_json({
            "type": "error",
            "message": "Missing conversation_id or new_name"
        })
        return

    try:
        success = state.conversation_manager.rename_conversation(conversation_id, new_name)
        if success:
            await websocket.send_json({
                "type": "info",
                "message": "Conversation renamed"
            })
            # Refresh conversation list
            conversations = state.conversation_manager.list_conversations()
            await websocket.send_json({
                "type": "conversations_list",
                "conversations": conversations
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": "Conversation not found"
            })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to rename: {str(e)}"
        })


async def handle_duplicate_conversation(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle duplicate conversation request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'conversation_id'
        state: Application state
    """
    conversation_id = data.get("conversation_id")

    if not conversation_id:
        await websocket.send_json({
            "type": "error",
            "message": "No conversation_id provided"
        })
        return

    try:
        new_id = state.conversation_manager.duplicate_conversation(
            conversation_id,
            available_tools=state.initial_tools
        )
        if new_id:
            await websocket.send_json({
                "type": "info",
                "message": "Conversation duplicated"
            })
            # Refresh conversation list
            conversations = state.conversation_manager.list_conversations()
            await websocket.send_json({
                "type": "conversations_list",
                "conversations": conversations
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": "Conversation not found"
            })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to duplicate: {str(e)}"
        })
