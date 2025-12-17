"""
Settings and configuration handlers.

Handles model changes, toggles, and workspace updates.
"""

import os
from fastapi import WebSocket
from app.state import AppState


async def handle_change_model(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle change model request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'provider' and 'model'
        state: Application state
    """
    try:
        provider = data.get("provider")
        model = data.get("model")

        if not provider or not model:
            await websocket.send_json({
                "type": "error",
                "message": "Provider and model required"
            })
            return

        # Import LLM classes
        from orchestral.llm import Claude, GPT, Gemini
        from orchestral.llm.ollama.client import Ollama
        from orchestral.llm.groq.client import Groq

        # Create new LLM instance based on provider
        if provider == "anthropic":
            new_llm = Claude(model=model)
        elif provider == "openai":
            new_llm = GPT(model=model)
        elif provider == "google":
            new_llm = Gemini(model=model)
        elif provider == "ollama":
            new_llm = Ollama(model=model)
        elif provider == "groq":
            new_llm = Groq(model=model)
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Unknown provider: {provider}"
            })
            return

        # Transfer tools from old LLM to new one
        new_llm.set_tools(state.agent.llm.tools)

        # Replace the agent's LLM
        state.agent.llm = new_llm

        # Remove the new model from non_streaming_models if present
        # This allows verified accounts to stream after model switch
        if model in state.non_streaming_models:
            state.non_streaming_models.discard(model)

        print(f"[App] Model changed to: {provider}/{model}")
        await websocket.send_json({
            "type": "info",
            "message": f"Model changed to {model}"
        })

    except Exception as e:
        print(f"[App] Model change error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to change model: {str(e)}"
        })


async def handle_toggle_model_names(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle toggle model names display.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'enabled'
        state: Application state
    """
    state.show_model_names = data.get("enabled", not state.show_model_names)
    # Update the agent_handler's reference
    if state.agent_handler:
        state.agent_handler.show_model_names_ref[0] = state.show_model_names
    print(f"[App] Model names display: {'enabled' if state.show_model_names else 'disabled'}")
    await websocket.send_json({
        "type": "info",
        "message": f"Model names {'shown' if state.show_model_names else 'hidden'}"
    })


async def handle_toggle_streaming(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle toggle streaming mode.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'enabled'
        state: Application state
    """
    state.streaming_enabled = data.get("enabled", not state.streaming_enabled)
    # Update the agent_handler's reference
    if state.agent_handler:
        state.agent_handler.streaming_enabled_ref[0] = state.streaming_enabled
    print(f"[App] Streaming: {'enabled' if state.streaming_enabled else 'disabled'}")
    await websocket.send_json({
        "type": "info",
        "message": f"Streaming {'enabled' if state.streaming_enabled else 'disabled'}"
    })


async def handle_toggle_cache(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle toggle prompt caching mode.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'enabled'
        state: Application state
    """
    enabled = data.get("enabled", True)
    # For now, just acknowledge the setting
    # Actual caching is controlled by the LLM provider
    print(f"[App] Prompt caching: {'enabled' if enabled else 'disabled'}")
    # Note: No action needed - this is just for UI state sync


async def handle_toggle_system_prompt(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle toggle system prompt display.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'enabled'
        state: Application state
    """
    state.show_system_prompt = data.get("enabled", not state.show_system_prompt)
    print(f"[App] System prompt display: {'enabled' if state.show_system_prompt else 'disabled'}")
    await websocket.send_json({
        "type": "info",
        "message": f"System prompt {'shown' if state.show_system_prompt else 'hidden'}"
    })


async def handle_set_system_prompt(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle set system prompt request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'system_prompt'
        state: Application state
    """
    new_system_prompt = data.get("system_prompt")

    if new_system_prompt is None:
        await websocket.send_json({
            "type": "error",
            "message": "System prompt required"
        })
        return

    # Update the agent's system prompt
    if state.agent:
        state.agent.set_system_prompt(new_system_prompt)
        print(f"[App] System prompt updated (length: {len(new_system_prompt)} chars)")
        await websocket.send_json({
            "type": "info",
            "message": "System prompt updated"
        })
    else:
        await websocket.send_json({
            "type": "error",
            "message": "No active agent"
        })


async def handle_get_system_prompt(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle get system prompt request.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    if state.agent:
        system_prompt = state.agent.system_prompt
        await websocket.send_json({
            "type": "system_prompt_info",
            "system_prompt": system_prompt
        })
    else:
        await websocket.send_json({
            "type": "error",
            "message": "No active agent"
        })


async def handle_reset_streaming_blocklist(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle reset streaming blocklist request.

    Note: This endpoint is kept for future use, but UI button was removed
    since auto-reset on model change handles most cases.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    state.non_streaming_models.clear()
    print(f"[App] Streaming blocklist cleared")
    await websocket.send_json({
        "type": "info",
        "message": "Streaming blocklist reset. All models will attempt streaming again."
    })


async def handle_update_base_directory(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle update base directory request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'base_directory'
        state: Application state
    """
    new_base_directory = data.get("base_directory")

    if not new_base_directory:
        await websocket.send_json({
            "type": "error",
            "message": "Base directory required"
        })
        return

    # Validate directory exists
    if not os.path.exists(new_base_directory):
        await websocket.send_json({
            "type": "error",
            "message": f"Directory does not exist: {new_base_directory}"
        })
        return

    # Update global base directory
    state.initial_base_directory = new_base_directory
    print(f"[App] Base directory updated: {new_base_directory}")

    # Recreate tools with new base directory for current conversation
    if state.agent and state.agent.llm:
        from app.tool_registry import serialize_tools, deserialize_tools

        # Get current tools configuration
        current_tools = state.agent.llm.tools
        tools_data = serialize_tools(current_tools)

        print(f"[App] Current tools data: {tools_data}")

        # Recreate tools with new base_directory
        new_tools = deserialize_tools(tools_data, new_base_directory)

        # Debug: check the new tools
        for tool in new_tools:
            if hasattr(tool, 'working_directory'):
                print(f"[App] Tool {tool.__class__.__name__} working_directory: {tool.working_directory}")

        # Update the LLM's tools
        state.agent.llm.set_tools(new_tools)

        print(f"[App] Recreated {len(new_tools)} tools with new base directory")

    await websocket.send_json({
        "type": "info",
        "message": "Workspace updated"
    })


async def handle_get_ollama_models(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle request to get available Ollama models.

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    try:
        from ollama import Client

        client = Client()
        models_list = client.list()

        # Extract model names
        model_names = [model.model for model in models_list.models]

        print(f"[App] Found {len(model_names)} Ollama models: {model_names}")

        await websocket.send_json({
            "type": "ollama_models",
            "models": model_names
        })

    except ImportError:
        print(f"[App] Ollama not installed")
        await websocket.send_json({
            "type": "ollama_models",
            "models": []
        })
    except Exception as e:
        print(f"[App] Failed to get Ollama models: {e}")
        await websocket.send_json({
            "type": "ollama_models",
            "models": []
        })


async def handle_get_tools_info(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle request to get tools information.

    Returns info about available tools (in current session) and requested tools
    (saved in conversation but not currently available).

    Args:
        websocket: WebSocket connection
        data: Message data (unused)
        state: Application state
    """
    try:
        # Get currently loaded tools from the agent (what's actually active now)
        current_tools = state.agent.llm.tools if state.agent and state.agent.llm else []

        # Get initial tools configured at startup (what's possible to enable)
        initial_tools = state.initial_tools or []

        # Initialize enabled_tools state if not already done
        if not state.enabled_tools:
            # Default: match current loaded tools
            state.enabled_tools = {tool.__class__.__name__: True for tool in current_tools}

        # Build available tools list (tools that exist in initial_tools)
        # Show their enabled state based on whether they're in current_tools
        available_tools = []
        current_tool_names = {tool.__class__.__name__ for tool in current_tools}

        for tool in initial_tools:
            tool_name = tool.__class__.__name__
            # A tool is enabled if it's in both enabled_tools dict AND currently loaded
            is_enabled = tool_name in current_tool_names and state.enabled_tools.get(tool_name, True)
            available_tools.append({
                "name": tool_name,
                "enabled": is_enabled,
                "available": True
            })

        # Build requested tools list (tools in loaded conversation but not in initial_tools)
        # These are tools that were saved in tools.json but aren't in the current session
        requested_tools = []
        available_tool_names = {tool.__class__.__name__ for tool in initial_tools}

        for tool_name in current_tool_names:
            if tool_name not in available_tool_names:
                requested_tools.append({
                    "name": tool_name,
                    "enabled": False,
                    "available": False
                })

        print(f"[App] Tools info - Available: {len(available_tools)}, Requested: {len(requested_tools)}")

        await websocket.send_json({
            "type": "tools_info",
            "available": available_tools,
            "requested": requested_tools
        })

    except Exception as e:
        print(f"[App] Failed to get tools info: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to get tools info: {str(e)}"
        })


async def handle_toggle_tool(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle tool enable/disable toggle.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'tool_name' and 'enabled'
        state: Application state
    """
    tool_name = data.get("tool_name")
    enabled = data.get("enabled")

    if tool_name is None or enabled is None:
        await websocket.send_json({
            "type": "error",
            "message": "Tool name and enabled state required"
        })
        return

    try:
        # Update enabled state
        state.enabled_tools[tool_name] = enabled

        # Get initial tools to find the tool instance
        initial_tools = state.initial_tools or []

        # Rebuild the agent's tools list based on enabled states
        new_tools = []
        for tool in initial_tools:
            if state.enabled_tools.get(tool.__class__.__name__, True):
                new_tools.append(tool)

        # Update the agent's LLM tools
        if state.agent and state.agent.llm:
            state.agent.llm.set_tools(new_tools)
            print(f"[App] Tool '{tool_name}' {'enabled' if enabled else 'disabled'}. Active tools: {len(new_tools)}")

        # Auto-save the conversation to persist tool changes
        if state.current_conversation_id and state.conversation_manager:
            from app.services import get_model_info
            model_info = get_model_info(state)

            state.conversation_manager.save_conversation(
                state.agent.context,
                conversation_id=state.current_conversation_id,
                model_info=model_info,
                tools=new_tools,  # Save updated tools list
                base_directory=state.initial_base_directory,
                preserve_tools=False  # Overwrite tools.json with new state
            )
            print(f"[App] Auto-saved tool changes to conversation {state.current_conversation_id}")

        await websocket.send_json({
            "type": "info",
            "message": f"Tool {'enabled' if enabled else 'disabled'}: {tool_name}"
        })

    except Exception as e:
        print(f"[App] Failed to toggle tool: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to toggle tool: {str(e)}"
        })


async def handle_set_max_cost(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle set max cost request.

    Args:
        websocket: WebSocket connection
        data: Message data containing 'max_cost' (number or None)
        state: Application state
    """
    max_cost = data.get("max_cost")

    if max_cost is not None:
        try:
            max_cost = float(max_cost)
            if max_cost < 0:
                await websocket.send_json({
                    "type": "error",
                    "message": "Max cost must be non-negative"
                })
                return
        except (ValueError, TypeError):
            await websocket.send_json({
                "type": "error",
                "message": "Invalid max cost value"
            })
            return

    # Update the agent handler's max cost
    if state.agent_handler:
        state.agent_handler.max_cost = max_cost
        # Reset the exceeded flag when max cost is updated
        state.agent_handler.cost_exceeded_interrupted = False

        if max_cost is None:
            print(f"[App] Max cost removed")
        else:
            print(f"[App] Max cost set to: ${max_cost:.2f}")

        await websocket.send_json({
            "type": "info",
            "message": f"Max cost {'removed' if max_cost is None else f'set to ${max_cost:.2f}'}"
        })
    else:
        await websocket.send_json({
            "type": "error",
            "message": "No active agent handler"
        })
