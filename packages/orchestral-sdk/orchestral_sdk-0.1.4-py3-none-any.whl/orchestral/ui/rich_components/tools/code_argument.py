from rich.console import Group
from rich.markdown import Markdown
from rich.text import Text
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.rich_components.tools.file_extentions import ext_to_name
from orchestral.ui.colors import LABEL_COLOR, CODE_THEME


class CodeArgumentToolPanel(BaseToolPanel):
    """
    Panel for displaying tools with code arguments.
    Detects arguments containing 'code' (e.g., VQC_code, python_code) and renders them with syntax highlighting.
    """

    def __init__(self, tool_name, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)
        self.tool_name = tool_name

    def _detect_language(self, arg_name):
        """
        Detect language from argument name.
        E.g., 'VQC_code' -> 'python' (default), 'python_code' -> 'python', 'js_code' -> 'javascript'
        Defaults to 'python' since 90% of code arguments are Python.
        """
        # Remove '_code' suffix and check if it's a known language
        if arg_name.lower().endswith('_code'):
            prefix = arg_name[:-5].lower()  # Remove '_code'
            if prefix in ext_to_name:
                return ext_to_name[prefix]
            # Check if it's already a language name
            if prefix in ext_to_name.values():
                return prefix

        # Check if it's just 'code' or starts with 'code_'
        if arg_name.lower() == 'code' or arg_name.lower().startswith('code_'):
            return 'python'

        # Default to Python for any other code argument
        return 'python'

    def display(self):
        """Display tool with code arguments syntax highlighted."""
        sections = []

        # Tool name header
        # tool_header = Text()
        # tool_header.append(" tool: ", style=LABEL_COLOR)
        # tool_header.append(self.tool_name)
        # sections.append(tool_header)

        # Process arguments
        code_args = []
        regular_args = []

        for arg_name, arg_value in self.args.items():
            if 'code' in arg_name.lower() and isinstance(arg_value, str):
                code_args.append((arg_name, arg_value))
            else:
                regular_args.append((arg_name, arg_value))

        # Display regular arguments first
        if regular_args:
            args_section = Text()
            args_section.append(" arguments:", style=LABEL_COLOR)
            sections.append(args_section)

            for arg_name, arg_value in regular_args:
                arg_line = Text()
                arg_line.append(f"   {arg_name}: ", style="gold3")
                # Truncate long values
                value_str = str(arg_value)
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                arg_line.append(value_str)
                sections.append(arg_line)

        # Display code arguments with syntax highlighting
        for arg_name, arg_value in code_args:
            # Add label for this code argument
            code_label = Text()
            code_label.append(f" {arg_name}:", style=LABEL_COLOR) # NOTE: You can put a newline here if needed before {arg_name}
            sections.append(code_label)

            # Detect language from argument name (defaults to Python)
            language = self._detect_language(arg_name)

            # Create markdown code block with syntax highlighting
            code_block = f"```{language}\n{arg_value}\n```"

            md = Markdown(code_block, code_theme=CODE_THEME)
            md_padded = Padding(md, pad=(0, 1, 0, 2))
            sections.append(md_padded)

        # Add output section if exists
        if not self.is_pending():
            output_label = Text()
            output_label.append("\n response:", style=LABEL_COLOR)
            sections.append(output_label)

            output_text = self.handle_ansi_output(self.output, apply_dim=False)
            output_padded = Padding(output_text, pad=(0, 0, 0, 3))
            sections.append(output_padded)
        else:
            # Show pending state
            output_label = Text()
            output_label.append("\n response:", style=LABEL_COLOR)
            sections.append(output_label)

            pending_text = self.handle_ansi_output(None, apply_dim=True)
            pending_padded = Padding(pending_text, pad=(0, 0, 0, 3))
            sections.append(pending_padded)

        group = Group(*sections)

        # Create panel with appropriate title
        title = f"ToolCall ─ {self.tool_name}"
        return self.create_panel(group, title)


if __name__ == "__main__":
    from rich.console import Console

    # Test with VQC_code
    vqc_code = """
def quantum_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
"""

    tool1 = CodeArgumentToolPanel(
        tool_name="execute_quantum",
        args={'VQC_code': vqc_code, 'shots': 1000},
        output="Execution successful",
        width=80
    )

    # Test with python_code
    python_code = """
def hello_world():
    print("Hello, World!")
    return 42
"""

    tool2 = CodeArgumentToolPanel(
        tool_name="run_script",
        args={'python_code': python_code},
        output=None,  # Pending
        width=80,
        is_streaming=True
    )

    console = Console()
    console.print(tool1.display())
    console.print(tool2.display())
