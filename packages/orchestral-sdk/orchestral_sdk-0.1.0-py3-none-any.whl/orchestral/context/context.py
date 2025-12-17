from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from typing import Optional, List, Iterable, Dict, Any
import json

class Context:
    """This is an object is a container for message objects and is passed to LLMs"""

    def __init__(self,
                 messages: Optional[List[Message | Response]] = None,
                 system_prompt: Optional[str] = None,
                 filepath: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):

        if messages is not None:
            self.messages = messages
            assert isinstance(self.messages, list)
        else:
            self.messages: list[Message | Response] = []
            self.set_system_prompt(system_prompt or "You are a helpful assistant.")

        # Initialize metadata dict for storing arbitrary data (e.g., tool state)
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}

        self.filepath = filepath

        if filepath is not None:
            self.load_json(filepath)

    def set_system_prompt(self, system_prompt: str):
        """Update the system prompt in the context."""
        # If messages attribute doesn't exist, create it
        if not hasattr(self, 'messages'):
            self.messages: list[Message|Response] = []
        
        for msg in self.messages:
            if isinstance(msg, Message) and msg.role == 'system':
                msg.text = system_prompt
                return
            
        self.messages.insert(0, Message(role='system', text=system_prompt))


    ### UTILS: 
    def add_message(self, message: Message | Response) -> None:
        self.messages.append(message)                                                    # type: ignore

    def get_messages(self) -> Iterable[Message]:
        for msg in self.messages:
            if isinstance(msg, Message):
                if msg:  # Filter out empty messages
                    yield msg
            elif isinstance(msg, Response):
                if msg.message:  # Filter out empty messages
                    yield msg.message

    def get_total_cost(self) -> float:
        """Get the total cost of all the Responses in USD"""
        costs = []
        for msg in self.messages:
            if isinstance(msg, Response):
                if msg.usage is not None:
                    costs.append(msg.usage.get_cost())
        return sum(costs)
        # return sum(msg.usage.get_cost() for msg in self.messages if isinstance(msg, Response))

    def get_total_tokens(self) -> int:
        """Get the total token count from the last Response.

        Returns:
            Total number of tokens from the most recent response.
            The last response's total_tokens already includes all input tokens
            from the conversation history, so we don't need to sum all responses.
        """
        # Find the last Response with usage
        for msg in reversed(self.messages):
            if isinstance(msg, Response) and msg.usage is not None:
                return msg.usage.tokens.get('total_tokens', 0)
        return 0

    ### CONTEXT MANAGEMENT:
    def copy(self):
        """Create a copy of this context with the same messages and metadata."""
        return Context(
            messages=self.messages.copy(),
            metadata=self.metadata.copy()  # Shallow copy of metadata dict
        )

    def compact(self):
        raise NotImplementedError

    def clear(self, preserve_system_prompt: bool = True):
        """Clear all messages from the context.

        Args:
            preserve_system_prompt (bool): If True, keep the first message if it's a system message (default True)
        """
        if preserve_system_prompt and self.messages:
            first_msg = self.messages[0]
            # Check if first message is a system message
            if isinstance(first_msg, Message) and first_msg.role == 'system':
                self.messages = [first_msg]
            elif isinstance(first_msg, Response) and first_msg.message.role == 'system':
                self.messages = [first_msg]
            else:
                self.messages = []
        else:
            self.messages = []

    def undo(self):
        """Remove the last user message and all subsequent messages (assistant responses, tool calls, etc.)

        Returns:
            bool: True if undo was successful, False if no user message found to undo
        """
        # Find the index of the last user message
        last_user_index = None
        for i in range(len(self.messages) - 1, -1, -1):
            msg = self.messages[i]
            if isinstance(msg, Message) and msg.role == 'user':
                last_user_index = i
                break
            elif isinstance(msg, Response) and msg.message.role == 'user':
                last_user_index = i
                break

        # If no user message found, can't undo
        if last_user_index is None:
            return False

        # Truncate messages to just before the last user message
        self.messages = self.messages[:last_user_index]
        return True

    def get_missing_tool_call_ids(self):
        required_ids = [] # Make a list of all the tool_call_ids expected by each message
        existing_ids = [] # Make a list of all the tool_call_ids already present
        for message in self.messages:
            if isinstance(message, Message):
                if message.role == 'tool':
                    existing_ids.append(message.tool_call_id)
            elif isinstance(message, Response):
                if message.message.role == 'assistant':
                    required_ids.extend(message.get_tool_call_ids())
            # Note: Currently only the assistant can make tool calls

        missing_ids = set(required_ids) - set(existing_ids)
        # assert not missing_ids, f'Missing IDs: {missing_ids}'
        return missing_ids

    def get_orphaned_tool_result_ids(self):
        """Get tool result IDs that don't have corresponding tool calls"""
        required_ids = [] # All tool_call_ids that were requested
        existing_ids = [] # All tool_call_ids that have results

        for message in self.messages:
            if isinstance(message, Message):
                if message.role == 'tool':
                    existing_ids.append(message.tool_call_id)
            elif isinstance(message, Response):
                if message.message.role == 'assistant':
                    required_ids.extend(message.get_tool_call_ids())

        orphaned_ids = set(existing_ids) - set(required_ids)
        return orphaned_ids

    def fix_missing_ids(self):
        missing_ids = self.get_missing_tool_call_ids()
        if missing_ids:
            print(f"WARNING: Adding placeholder responses for {len(missing_ids)} missing tool call(s)")

        # For each missing tool call, find where it was called and insert the result immediately after
        for id in missing_ids:
            # Find the Response that contains this tool call
            insert_index = None
            for i, msg in enumerate(self.messages):
                if isinstance(msg, Response) and msg.message.role == 'assistant':
                    if id in msg.get_tool_call_ids():
                        # Insert the tool result right after this Response
                        insert_index = i + 1
                        break

            dummy_message = Message(
                role='tool',
                tool_call_id=id,
                text='ToolError: Tool execution was interrupted'
            )

            if insert_index is not None:
                # Insert at the correct position (right after the tool_use)
                self.messages.insert(insert_index, dummy_message)
            else:
                # Fallback: append to end if we can't find the tool call (shouldn't happen)
                self.add_message(dummy_message)

        assert len(self.get_missing_tool_call_ids()) == 0, f'fix_missing_ids was unsuccessful!'

    def fix_orphaned_results(self):
        """Remove tool result messages that don't have corresponding tool calls"""
        orphaned_ids = self.get_orphaned_tool_result_ids()
        if orphaned_ids:
            print(f"WARNING: Removing {len(orphaned_ids)} orphaned tool result(s)")
            # Filter out messages with orphaned tool_call_ids
            self.messages = [
                msg for msg in self.messages
                if not (isinstance(msg, Message) and msg.role == 'tool' and msg.tool_call_id in orphaned_ids)
            ]
        assert len(self.get_orphaned_tool_result_ids()) == 0, f'fix_orphaned_results was unsuccessful!'

    def fix_tool_call_mismatches(self):
        """Fix both missing and orphaned tool calls/results.

        This method should be called to ensure context validity:
        - Removes orphaned tool results (results without corresponding tool calls)
        - Adds placeholder results for missing tool calls (calls without results)
        """
        self.fix_orphaned_results()
        self.fix_missing_ids()

    ### LOAD / SAVE:
    def to_dict(self) -> dict:
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata  # Include metadata in serialization
        }

    def from_dict(self, data: dict):
        self.messages = []
        for msg in data.get("messages", []):
            if msg.get("type") == "response":
                self.messages.append(Response.from_dict(msg))
            else:
                self.messages.append(Message.from_dict(msg))

        # Load metadata if present, gracefully handle missing metadata
        self.metadata = data.get("metadata", {})

    def save_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_json(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.from_dict(data)

    ### UNDER THE HOOD
    def __repr__(self) -> str:
        return f"Context(messages={self.messages})"
    
    def __str__(self) -> str:
        s = f"Context with {len(self.messages)} messages:"
        for msg in self.messages:
            if isinstance(msg, Message):
                s += f"\n  {msg}"
            elif isinstance(msg, Response):
                s += f"\n  {msg.message}"
        return s

    def __iter__(self):
        # NOTE: Don't use this since the output could be either a Response or a Message
        return iter(self.messages)

    def __len__(self) -> int:
        return len(self.messages)

    def __getitem__(self, idx: int) -> Message | Response:
        return self.messages[idx]