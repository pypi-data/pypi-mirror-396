from typing import List
from pydantic import Field
from pydantic.fields import FieldInfo

def RuntimeField(**kwargs):
    """Create a field that's required at runtime but optional for instantiation."""
    # Allow custom defaults but default to None if not specified
    if 'default' not in kwargs:
        kwargs['default'] = None
    return Field(json_schema_extra={"runtime": True}, **kwargs)

def StateField(**kwargs):
    """Create a field that's maintained by the tool (excluded from runtime)."""
    return Field(json_schema_extra={"runtime": False}, **kwargs)

def is_state_field(field_info: FieldInfo) -> bool:
    """Check if a Pydantic field is a StateField."""
    json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}
    return json_schema_extra.get('runtime') == False

def assert_runtime_fields_present(tool_instance, runtime_fields: List[str]) -> None:
    """Assert that runtime fields are not None - helps with type checking."""
    for field_name in runtime_fields:
        value = getattr(tool_instance, field_name)
        assert value is not None, f"Runtime field {field_name} should not be None"