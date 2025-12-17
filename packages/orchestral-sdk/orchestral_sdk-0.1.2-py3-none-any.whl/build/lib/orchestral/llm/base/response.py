from typing import Optional
from orchestral.context.message import Message
from orchestral.llm.base.usage import Usage


class Response:
    def __init__(self, 
            model,
            message_choices: Optional[list[Message]]=None, 
            message: Optional[Message]=None,
            usage: Optional[Usage]=None, id=None
    ):
        self.model = model
        self.usage = usage
        self.id = id

        if message_choices:
            self.message_choices = message_choices
            self.message = message_choices[0]
        elif message is not None:
            self.message = message
        else:
            raise ValueError("Either message_choices or message must be provided.")

    def get_tool_call_ids(self):
        return self.message.get_tool_call_ids()

    def __repr__(self):
        return f"Response(model={self.model}, messages={self.message}, usage={self.usage}, id={self.id})"

    
    def to_dict(self):
        return {
            "type": "response",
            "model": self.model,
            "message": self.message.to_dict() if self.message else None,
            "usage": self.usage.to_dict() if self.usage else None,
            "id": self.id
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Response object from a dictionary.
        Note: We do not restore message_choices here, only the primary message.
        Note: We do not restore the pricing model only the total cost.
        """
        message = Message.from_dict(data["message"])
        usage = Usage.from_dict(data["usage"]) if data.get("usage") else None
        return cls(
            model=data["model"],
            message=message,
            usage=usage,
            id=data.get("id")
        )