from typing import Dict, Any

class ToolSpec:
    """Provider-agnostic tool specification - the 'interlingua' for tools."""
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description  
        self.input_schema = input_schema
        
    def __repr__(self):
        return f"ToolSpec(name={self.name}, description={self.description[:50]}...)"