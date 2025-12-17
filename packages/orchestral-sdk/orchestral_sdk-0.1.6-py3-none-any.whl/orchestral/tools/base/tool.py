from abc import abstractmethod
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field, ValidationError

from orchestral.tools.base.field_utils import assert_runtime_fields_present
from orchestral.tools.base.schema_generator import SchemaGenerator
from orchestral.tools.base.tool_spec import ToolSpec

class BaseTool(BaseModel):
    """Base class for all tools in Orchestral AI."""
    
    # Tool metadata
    cost: float = Field(default=0.0, exclude=True, description="Cost to run this tool")

    class Config:
        validate_assignment = True
        # Allow extra fields for extensibility
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup()

    def _setup(self):
        """Override this method to add custom tool setup logic after field initialization.

        Use StateField for any configuration parameters you need access to here.
        Example:
            initial_content: str = StateField(default="", description="Starting content")

        Then access them in _setup():
            def _setup(self):
                self.notepad = self.initial_content
        """
        pass

    @classmethod
    def _get_runtime_fields(cls) -> List[str]:
        """Auto-detect runtime fields by finding fields that should be provided by LLM."""
        return SchemaGenerator.detect_runtime_fields(cls)

    @classmethod
    def _get_required_fields(cls) -> List[str]:
        """Get only the runtime fields that are required (no defaults)."""
        return SchemaGenerator.generate_input_schema(cls)["required"]

    @classmethod
    def _get_state_fields(cls) -> List[str]:
        """Get all StateField names for this tool."""
        state_fields = []

        # Get all model fields
        for field_name, field_info in cls.model_fields.items():
            # Skip base tool fields
            if field_name in ['cost']:
                continue

            # Check if this is a StateField
            json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}
            is_state_field = json_schema_extra.get('runtime') == False

            if is_state_field:
                state_fields.append(field_name)

        return state_fields

    def _extract_state_field_values(self) -> Dict[str, Any]:
        """Extract current values of all StateFields."""
        state_fields = self._get_state_fields()
        return {field_name: getattr(self, field_name) for field_name in state_fields}

    def _restore_state_field_values(self, state_values: Dict[str, Any]) -> None:
        """Restore StateField values to this instance."""
        for field_name, value in state_values.items():
            setattr(self, field_name, value)

    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        """Generate input schema for LLM function calling."""
        return SchemaGenerator.generate_input_schema(cls)

    @classmethod
    def get_tool_spec(cls) -> ToolSpec:
        """Get provider-agnostic tool specification."""
        return SchemaGenerator.generate_tool_spec(cls)

    @classmethod
    def get_name(cls) -> str:
        """Get the tool name as it appears to LLMs."""
        return cls.__name__.replace("Tool", "").lower()

    def format_error(self, error: str, reason: str = "", context: str = "", suggestion: str = "") -> str:
        """Formats errors in a structured way for LLMs."""
        message = f"Error: {error}"
        if reason:
            message += f"\n- Reason: {reason}"
        if context:
            message += f"\n- Context: {context}"
        if suggestion:
            message += f"\n- {suggestion}"
        return message

    def execute(self, stream_callback: Optional[Callable[[str], None]] = None, **kwargs) -> str:
        """Execute the tool with validation and state safety.

        Args:
            stream_callback: Optional callback for streaming output updates.
                            Called with partial output as tool executes.
            **kwargs: Runtime field values for the tool

        Returns:
            Final tool output as string
        """
        runtime_fields = self._get_runtime_fields()
        required_fields = self._get_required_fields()

        # Validate that all required fields are provided
        missing = [f for f in required_fields if f not in kwargs]
        if missing:
            return self.format_error(
                error="Missing Required Fields",
                reason=f"Missing: {missing}",
                suggestion=f"Provide all required fields: {required_fields}"
            )

        # Save current StateFields (these should persist across execution)
        state_field_values = self._extract_state_field_values()

        # Save current state for rollback on failure (including StateFields for now)
        original_state = self.model_dump()

        try:
            # Create a copy of current instance with runtime data
            current_data = self.model_dump()
            current_data.update(kwargs)

            # Validate the combined data
            updated_instance = self.__class__(**current_data)

            # Restore StateField values to the validated instance
            updated_instance._restore_state_field_values(state_field_values)

            # Update self with validated data (only runtime fields)
            for field_name in runtime_fields:
                value = getattr(updated_instance, field_name)
                # Ensure runtime fields are not None after validation
                assert value is not None, f"Runtime field {field_name} should not be None after validation"
                setattr(self, field_name, value)

            # Restore StateField values to self as well
            self._restore_state_field_values(state_field_values)

            # Assert all runtime fields are present (helps type checker in _run method)
            assert_runtime_fields_present(self, runtime_fields)

            # Store callback for tool to use (optional)
            self._stream_callback = stream_callback

            # Run the tool - this is where failures can happen
            result = self._run()

            # Clean up callback reference
            if hasattr(self, '_stream_callback'):
                delattr(self, '_stream_callback')

            # Success - return result
            return str(result) if result is not None else ""

        except ValidationError as e:
            # Validation failed - restore StateFields and return error
            self._restore_state_field_values(state_field_values)
            # Clean up callback on error
            if hasattr(self, '_stream_callback'):
                delattr(self, '_stream_callback')
            return self.format_error(
                error="Validation Error",
                reason=str(e),
                suggestion="Check parameter types and values"
            )
        except Exception as e:
            # Execution failed - rollback runtime fields but preserve StateFields
            self._rollback_state(original_state)
            self._restore_state_field_values(state_field_values)
            # Clean up callback on error
            if hasattr(self, '_stream_callback'):
                delattr(self, '_stream_callback')
            return self.format_error(
                error="Execution Error",
                reason=str(e),
                suggestion="Check tool implementation"
            )
    
    def _rollback_state(self, saved_state: Dict[str, Any]) -> None:
        """Restore tool to a previous state."""
        for field_name, value in saved_state.items():
            setattr(self, field_name, value)

    @abstractmethod
    def _run(self) -> Any:
        """Implement the tool's main logic. Access validated inputs via self attributes."""
        pass