from typing import List, Dict, Any, Type
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from orchestral.tools.base.tool_spec import ToolSpec

class SchemaGenerator:
    """Handles runtime field detection and schema generation for tools."""
    
    @staticmethod
    def detect_runtime_fields(tool_class: Type[BaseModel]) -> List[str]:
        """Auto-detect runtime fields by finding fields that should be provided by LLM."""
        runtime_fields = []
        
        # Get all model fields
        for field_name, field_info in tool_class.model_fields.items():
            # Skip base tool fields 
            if field_name in ['cost']:
                continue
                
            # Check field markers
            json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}
            is_state_field = json_schema_extra.get('runtime') == False
            is_runtime_field = json_schema_extra.get('runtime') == True
            
            if is_state_field:
                continue  # Skip explicitly marked state fields
                
            if is_runtime_field:
                runtime_fields.append(field_name)  # Explicitly marked runtime field
                continue
            
            # Auto-detect: fields without meaningful defaults are runtime fields
            has_meaningful_default = (
                # Has explicit non-None default (like 0, "hello", etc.)
                (field_info.default is not None and field_info.default != PydanticUndefined and field_info.default != None) or
                # Has a default factory
                field_info.default_factory is not None
            )
            
            if not has_meaningful_default:
                runtime_fields.append(field_name)
                
        return runtime_fields

    @staticmethod
    def generate_input_schema(tool_class: Type[BaseModel]) -> Dict[str, Any]:
        """Generate input schema for LLM function calling."""
        runtime_fields = SchemaGenerator.detect_runtime_fields(tool_class)
        
        # Allow tools with no runtime fields (e.g., GetTimeTool)
        if not runtime_fields:
            return {
                "type": "object",
                "properties": {},
                "required": []
            }
        
        full_schema = tool_class.model_json_schema()
        props = full_schema.get("properties", {})
        
        # Separate required vs optional runtime fields
        required_fields = []
        filtered_props = {}
        
        for field_name in runtime_fields:
            if field_name not in props:
                raise ValueError(f"Runtime field '{field_name}' not found in schema for {tool_class.__name__}")
            
            field_info = props[field_name].copy()
            
            # Check if field has a meaningful default (making it optional)
            field_obj = tool_class.model_fields[field_name]
            has_meaningful_default = (
                field_obj.default is not None and 
                field_obj.default != PydanticUndefined and 
                field_obj.default != None
            ) or field_obj.default_factory is not None
            
            # Only add to required if no meaningful default
            if not has_meaningful_default:
                required_fields.append(field_name)
            
            # Handle Optional types (remove anyOf and default)
            if "anyOf" in field_info:
                for type_def in field_info["anyOf"]:
                    if type_def.get("type") != "null":
                        field_info.update(type_def)
                        break
                field_info.pop("anyOf", None)
            
            # Remove unwanted fields (default, title, runtime markers)
            field_info.pop("default", None)
            field_info.pop("title", None)
            field_info.pop("runtime", None)
            filtered_props[field_name] = field_info

        return {
            "type": "object",
            "properties": filtered_props,
            "required": required_fields,
        }

    @staticmethod
    def generate_tool_spec(tool_class: Type[BaseModel]) -> ToolSpec:
        """Get provider-agnostic tool specification."""
        tool_name = tool_class.__name__.replace("Tool", "").lower()
        description = tool_class.__doc__ or f"Tool: {tool_name}"
        
        return ToolSpec(
            name=tool_name,
            description=description.strip(),
            input_schema=SchemaGenerator.generate_input_schema(tool_class)
        )