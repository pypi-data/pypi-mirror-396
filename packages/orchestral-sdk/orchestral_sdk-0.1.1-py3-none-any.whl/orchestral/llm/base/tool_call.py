

class ToolCall:
    def __init__(self, id, tool_name: str, arguments: dict):
        self.id = id
        self.tool_name = tool_name
        self.arguments = arguments

    def __str__(self):
        return f"ToolCall(called: {self.tool_name}(**{self.arguments}), id={self.id})"

    def __repr__(self):
        return self.__str__()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "arguments": self.arguments
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            tool_name=data.get("tool_name"),
            arguments=data.get("arguments", {})
        )