from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField

class MultiplyTool(BaseTool):
    """Multiply two numbers together"""
    
    a: float | None = RuntimeField(description="First number to multiply")
    b: float | None = RuntimeField(description="Second number to multiply")
    
    def _run(self) -> float:
        """Multiply the two numbers."""  # <-- NOTE: This docstring is not seen by the agent.
        return self.a * self.b           # type: ignore