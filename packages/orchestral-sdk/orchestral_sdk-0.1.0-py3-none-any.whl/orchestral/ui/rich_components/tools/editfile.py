import difflib
from rich.console import Group
from rich.text import Text
from rich.syntax import Syntax
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR, FAILED_COLOR, CODE_THEME


class EditFileToolPanel(BaseToolPanel):
    """Custom panel for EditFileTool showing a unified diff."""

    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display(self):
        """Display edit operation with unified diff format."""
        # Show file path
        path = self.args.get("path", "(no path)")

        # Build header
        header = Text()
        header.append(" file: ", style=LABEL_COLOR)
        header.append(path)
        header.append("\n")

        # If pending, show simple message
        if self.is_pending():
            status = Text("editing...", style="dim")
            group = Group(header, Padding(status, pad=(0, 0, 0, 2)))
            return self.create_panel(group, "EditFile")

        # Check if output is an error (either is_failed flag or output starts with "Error:")
        is_error = self.failed() or (self.output and self.output.strip().startswith("Error:"))

        if is_error:
            # Show error message with red border
            error_text = Text.from_ansi(self.output if self.output else "Unknown error")
            group = Group(header, Padding(error_text, pad=(0, 0, 0, 2)))
            return self.create_panel(group, "EditFile", border_style=FAILED_COLOR)

        # Success - show unified diff
        old_string = self.args.get("old_string", "")
        new_string = self.args.get("new_string", "")
        replace_all = self.args.get("replace_all", False)

        # Generate unified diff
        old_lines = old_string.splitlines()
        new_lines = new_string.splitlines()

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{path} (before)",
            tofile=f"{path} (after)",
            lineterm=''
        )

        diff_text = '\n'.join(diff)

        # Apply syntax highlighting to diff
        diff_syntax = Syntax(
            diff_text,
            "diff",
            theme=CODE_THEME,
            line_numbers=False,
            word_wrap=True,
            # background_color="default"
        )

        # Add metadata about operation
        metadata = Text()
        if replace_all:
            assert isinstance(self.output, str), "Expected tool output to be a string on success"
            # Parse output to get count
            if "Replaced" in self.output: 
                metadata.append(" ", style=LABEL_COLOR)
                metadata.append(self.output.split('\n')[0])  # First line has count
        else:
            metadata.append(" ", style=LABEL_COLOR)
            metadata.append("replaced 1 occurrence")

        # Combine elements
        group = Group(
            header,
            metadata,
            Text(""),  # Blank line
            Padding(diff_syntax, pad=(0, 1, 0, 2))
        )

        return self.create_panel(group, "EditFile")


if __name__ == "__main__":
    from rich.console import Console

    # Test successful edit
    args = {
        "path": "math_operations.py",
        "old_string": '    """\n    Adds two numbers together.\n\n    :param a: First number\n    :param b: Second number\n    :return: Sum of a and b\n    """',
        "new_string": '    """\n    Adds two numbers together with enhanced precision.\n\n    :param a: First numeric input\n    :param b: Second numeric input\n    :return: Precise sum of a and b\n    :raises TypeError: If inputs are not numeric\n    """',
        "replace_all": False
    }
    output = "Success: Replaced 1 occurrence in 'math_operations.py'\nFile now has 77 lines (+1 lines)"

    console = Console()
    panel = EditFileToolPanel(args, output, width=100)
    console.print(panel.display())

    # Test pending state
    panel_pending = EditFileToolPanel(args, None, width=100, is_streaming=True)
    console.print(panel_pending.display())

    # Test failed state
    error_output = "Error: File Not Found\nReason: The specified file does not exist"
    panel_failed = EditFileToolPanel(args, error_output, width=100, is_failed=True)
    console.print(panel_failed.display())
