import re
from orchestral.llm.base.tool_call import ToolCall
from typing import Optional

class Message:
    """This is an abstraction which encapsulates messages and all their metadata.
    It provides a unified structure for working with message from different models.
    Different LLMs expect different formats, and should have a custom interpreter which turns this into the appropriate format for the model.

    This also encapsulates tool results, which are a special type of message."""

    def __init__(self, 
            role: Optional[str],
            text: Optional[str] = None,
            reasoning: Optional[str] = None,
            audio: Optional[str] = None,
            function_call: Optional[str] = None,
            tool_calls: Optional[list[ToolCall]] = None,
            annotations: Optional[list[str]] = None,
            refusal=None,
            tool_call_id=None,
            failed=False,
        ):

        self.role = role
        self.text = text
        self.reasoning = reasoning
        self.audio = audio
        self.function_call = function_call
        self.tool_calls = tool_calls
        self.annotations = annotations if annotations else [] # TODO: Figure out how to handle annotations
        self.refusal = refusal
        self.failed = failed

        self.metadata = {}

        # Enforce tool_call_id rules
        if role != 'tool' and tool_call_id is not None:
            raise ValueError("tool_call_id can only be set for tool messages")
        elif role == 'tool' and tool_call_id is None:
            raise ValueError("tool_call_id must be set for tool messages")
        self.tool_call_id = tool_call_id

    def get_tool_call_ids(self):
        """Check if this messages has tool call IDs"""
        if not self.tool_calls:
            return []
        else:
            return [call.id for call in self.tool_calls]

    def __bool__(self):
        """Check if message has any content.

        Returns True if the message contains any meaningful content:
        - Non-empty text
        - Audio data
        - Function call
        - Tool calls
        - Refusal

        Returns False for completely empty messages.
        """
        # Check for text (must be non-empty and not just whitespace)
        if self.text and self.text.strip():
            return True

        # Check for other content types
        if self.reasoning or self.audio or self.function_call or self.tool_calls or self.refusal:
            return True

        return False

    def __repr__(self):
        text = 'Message('
        if self.role:
            text += f'role={self.role}, '
        if self.text:
            text += f'text={self.text}, '
        if self.reasoning:
            text += f'reasoning={self.reasoning}, '
        if self.tool_calls:
            text += f'tool_calls={self.tool_calls}, '
        if self.tool_call_id:
            text += f'tool_call_id={self.tool_call_id[:7]}...{self.tool_call_id[-3:]}, '
        if self.metadata:
            text += f'metadata={self.metadata}, '
        text = text.rstrip(', ') + ')'
        return text
    
        # Old versions: 
        # return f"Message(role={self.role}, text={self.text}, metadata={self.metadata})"
        # return self.__str__()

    def __str__(self):
        role = f'[{self.role}]: '.rjust(14)
        if self.role == 'user':
            return role + self.text # type: ignore
        elif self.role == 'assistant':
            result = role
            if self.text:
                result += self.text
                if self.reasoning:
                    result += f"\n{' ' * 16}(reasoning={self.reasoning})"
                if self.tool_calls:
                    result += f"\n{' ' * 16}(tool_calls={self.tool_calls})"
                return result
            if self.tool_calls:
                result += f"(tool_calls={self.tool_calls})"
            return result
        elif self.role == 'system':
            return role + self.text # type: ignore
        elif self.text and self.role == 'tool':
            result = self.text.strip(' \n')
            formatted_result = re.sub(r'\n+', '\n', result)
            return role + f"result='{formatted_result}' (tool_call_id={self.tool_call_id})" +  '\n' # type: ignore
        else:
            raise ValueError(f'Something went wrong printing message: role={self.role}, text={self.text}')



    def to_dict(self) -> dict:
        data = {
            "type": "message",
            "role": self.role,
            "text": self.text,
            "reasoning": self.reasoning,
            "audio": self.audio,
            "function_call": self.function_call,
            "tool_calls": [call.to_dict() for call in self.tool_calls] if self.tool_calls else None,
            "annotations": self.annotations,
            "refusal": self.refusal,
            "tool_call_id": self.tool_call_id,
            "metadata": self.metadata,
            "failed": self.failed
        }
        # Remove keys with None values
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict):
        if data.get("type") != "message":
            raise ValueError("Invalid data: Not a message")

        tool_calls = [ToolCall.from_dict(tc) for tc in data.get("tool_calls", [])] if "tool_calls" in data else None

        message = cls(
            role=data.get("role"),
            text=data.get("text"),
            reasoning=data.get("reasoning"),
            audio=data.get("audio"),
            function_call=data.get("function_call"),
            tool_calls=tool_calls,
            annotations=data.get("annotations", []),
            refusal=data.get("refusal"),
            tool_call_id=data.get("tool_call_id"),
            failed=data.get("failed", False)
        )
        message.metadata = data.get("metadata", {})
        return message