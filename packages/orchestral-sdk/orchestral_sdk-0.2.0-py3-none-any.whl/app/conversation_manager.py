"""Conversation management for saving/loading/listing conversations."""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from orchestral import Agent, define_tool
from orchestral.llm import Groq
from orchestral.context.context import Context
from orchestral.tools.base.tool import BaseTool
from app.tool_registry import serialize_tools, deserialize_tools


class ConversationManager:
    """Manages conversation persistence with metadata."""

    def __init__(self, conversations_dir: str = "conversations"):
        self.conversations_dir = Path(conversations_dir)
        self.conversations_dir.mkdir(exist_ok=True)

    def _get_conversation_path(self, conversation_id: str) -> Path:
        """Get the path to a conversation directory."""
        return self.conversations_dir / conversation_id

    def _get_timestamp_id(self) -> str:
        """Generate a timestamp-based ID for a new conversation."""
        return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    def _format_relative_time(self, timestamp: str) -> str:
        """Format timestamp as relative time (e.g., '34m ago', '3h ago', '2d ago')."""
        try:
            # Parse timestamp format: 2025-10-29T14-30-45
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H-%M-%S")
            delta = datetime.now() - dt

            seconds = int(delta.total_seconds())
            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes}m ago"
            elif seconds < 86400:
                hours = seconds // 3600
                return f"{hours}h ago"
            else:
                days = seconds // 86400
                return f"{days}d ago"
        except Exception as e:
            return "unknown"

    def save_conversation(
        self,
        context: Context,
        conversation_id: Optional[str] = None,
        name: Optional[str] = None,
        model_info: Optional[Dict] = None,
        tools: Optional[List[BaseTool]] = None,
        base_directory: Optional[str] = None,
        preserve_tools: bool = False
    ) -> str:
        """Save a conversation with metadata.

        Args:
            context: The context to save
            conversation_id: Optional existing ID, or None to create new
            name: Optional name for the conversation
            model_info: Optional dict with 'provider' and 'model' keys
            tools: Optional list of tools to save
            base_directory: Optional base directory for file tools
            preserve_tools: If True, don't overwrite existing tools.json (preserves original tool set)

        Returns:
            The conversation ID
        """
        # Create new ID if none provided
        # Load or initialize metadata
        existing_name = None
        if conversation_id is None:
            conversation_id = self._get_timestamp_id()
            created_at = conversation_id
        else:
            # Load existing metadata to preserve created_at and name
            conv_path = self._get_conversation_path(conversation_id)
            metadata_path = conv_path / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    existing_metadata = json.load(f)
                    created_at = existing_metadata.get('created_at', conversation_id)
                    existing_name = existing_metadata.get('name')
            else:
                created_at = conversation_id

        # Create conversation directory
        conv_path = self._get_conversation_path(conversation_id)
        conv_path.mkdir(exist_ok=True)

        # Save context
        context_path = conv_path / "context.json"
        context.save_json(str(context_path))

        # Save metadata
        # If name is None, preserve existing name or use default for new conversations
        final_name = name if name is not None else (existing_name or "New Conversation")
        metadata = {
            "id": conversation_id,
            "name": final_name,
            "created_at": created_at,
            "updated_at": self._get_timestamp_id()
        }

        # Add model info if provided
        if model_info:
            metadata["model"] = model_info

        # Add base_directory if provided
        if base_directory:
            metadata["base_directory"] = base_directory

        metadata_path = conv_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        # Save tools if provided (unless preserve_tools is True)
        if tools and not preserve_tools:
            tools_data = serialize_tools(tools)
            tools_path = conv_path / "tools.json"
            with open(tools_path, 'w') as f:
                json.dump({"tools": tools_data}, f, indent=4)

        return conversation_id

    def load_conversation(
        self,
        conversation_id: str,
        available_tools: Optional[List[BaseTool]] = None
    ) -> tuple[Context, Dict, Optional[List[BaseTool]]]:
        """Load a conversation and its metadata.

        Args:
            conversation_id: The ID of the conversation to load
            available_tools: Optional list of tools available in current session.
                           Used for introspection-based tool matching by class name.

        Returns:
            Tuple of (context, metadata, tools)
        """
        conv_path = self._get_conversation_path(conversation_id)

        # Load context
        context_path = conv_path / "context.json"
        context = Context(filepath=str(context_path))

        # Load metadata
        metadata_path = conv_path / "metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Load tools if they exist
        tools = None
        tools_path = conv_path / "tools.json"
        if tools_path.exists():
            with open(tools_path, 'r') as f:
                tools_data = json.load(f)

            # Get base_directory from metadata
            base_directory = metadata.get("base_directory", ".")
            tools = deserialize_tools(
                tools_data.get("tools", []),
                base_directory,
                available_tools=available_tools,
                conversation_id=conversation_id
            )

        return context, metadata, tools

    def list_conversations(self) -> List[Dict]:
        """List all conversations with metadata.

        Returns:
            List of metadata dicts sorted by updated_at (most recent first)
        """
        conversations = []

        for conv_dir in self.conversations_dir.iterdir():
            if not conv_dir.is_dir():
                continue

            metadata_path = conv_dir / "metadata.json"
            if not metadata_path.exists():
                continue

            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Add relative time
            metadata['relative_time'] = self._format_relative_time(
                metadata.get('updated_at', metadata.get('created_at', ''))
            )
            conversations.append(metadata)

        # Sort by updated_at (most recent first)
        conversations.sort(
            key=lambda x: x.get('updated_at', x.get('created_at', '')),
            reverse=True
        )

        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if deleted, False if not found
        """
        conv_path = self._get_conversation_path(conversation_id)

        if not conv_path.exists():
            return False

        # Delete all files in the directory
        for file in conv_path.iterdir():
            file.unlink()

        # Delete the directory
        conv_path.rmdir()

        return True

    def rename_conversation(self, conversation_id: str, new_name: str) -> bool:
        """Rename a conversation.

        Args:
            conversation_id: The ID of the conversation to rename
            new_name: The new name for the conversation

        Returns:
            True if renamed, False if not found
        """
        conv_path = self._get_conversation_path(conversation_id)
        metadata_path = conv_path / "metadata.json"

        if not metadata_path.exists():
            return False

        # Load existing metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Update name and timestamp
        metadata['name'] = new_name
        metadata['updated_at'] = self._get_timestamp_id()

        # Save updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        return True

    def duplicate_conversation(
        self,
        conversation_id: str,
        available_tools: Optional[List[BaseTool]] = None
    ) -> Optional[str]:
        """Duplicate a conversation.

        Args:
            conversation_id: The ID of the conversation to duplicate
            available_tools: Optional list of tools available in current session

        Returns:
            The new conversation ID, or None if original not found
        """
        conv_path = self._get_conversation_path(conversation_id)

        if not conv_path.exists():
            return None

        # Load the conversation
        context, metadata, tools = self.load_conversation(conversation_id, available_tools)

        # Create new ID for duplicate
        new_id = self._get_timestamp_id()

        # Save as new conversation with modified name
        new_name = f"{metadata.get('name', 'Untitled')} (Copy)"
        self.save_conversation(
            context,
            conversation_id=new_id,
            name=new_name,
            model_info=metadata.get("model"),
            tools=tools,
            base_directory=metadata.get("base_directory")
        )

        return new_id

    def generate_conversation_name(self, context: Context) -> str:
        """Generate a short descriptive name for a conversation using an agent.

        Args:
            context: The conversation context

        Returns:
            A short descriptive name (2-5 words)
        """
        # Define the propose_name tool
        @define_tool()
        def propose_name(name: str):
            """Propose a short, descriptive name for this conversation (2-5 words).
            If the conversation is totally generic and has no unique features, return "New Conversation".

            Args:
                name: The proposed name for the conversation
            """
            return f"Proposed: {name}"

        # Create a temporary agent with a copy of the context
        temp_context = context.copy()

        from orchestral.llm import CheapLLM
        llm = CheapLLM()

        # Log which LLM was selected for debugging
        llm_name = llm.__class__.__name__
        llm_model = getattr(llm, 'model', 'unknown')
        print(f"[App] Generating conversation name using {llm_name} ({llm_model})")

        naming_agent = Agent(
            llm=llm,
            context=temp_context,
            tools=[propose_name],  # Already an instance (decorator returns instance)
            system_prompt="You are a conversation naming assistant. Based on the conversation history, propose a short, descriptive name (2-5 words) using the propose_name tool."
        )

        # Ask for a name
        naming_agent.run("Propose a short, descriptive name for this conversation based on its content.")

        # Extract the proposed name from the tool result
        # The tool result is in the second-to-last message
        tool_result = naming_agent.context.messages[-2].text

        # Parse out the name from "Proposed: {name}"
        if tool_result and tool_result.startswith("Proposed: "):
            name = tool_result.replace("Proposed: ", "").strip()
            return name

        return "New Conversation"
