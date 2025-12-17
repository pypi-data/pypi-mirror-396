from rich.console import Group
from rich.text import Text
from rich.padding import Padding
from rich.syntax import Syntax

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR


class FileSearchToolPanel(BaseToolPanel):
    """Custom panel for FileSearchTool with syntax-highlighted output."""

    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display(self):
        """Display file search results with proper formatting."""
        # Build header with search parameters
        pattern = self.args.get("pattern", "(no pattern)")
        file_pattern = self.args.get("file_pattern", "*")
        output_mode = self.args.get("output_mode", "count")
        case_sensitive = self.args.get("case_sensitive", True)

        header = Text()
        header.append(" pattern: ", style=LABEL_COLOR)
        header.append(f"{pattern}")

        if file_pattern != "*":
            header.append("\n files: ", style=LABEL_COLOR)
            header.append(f"{file_pattern}")

        header.append("\n mode: ", style=LABEL_COLOR)
        header.append(f"{output_mode}")

        if not case_sensitive:
            header.append(" (case-insensitive)", style="dim")

        # If pending, show searching message
        if self.is_pending():
            status = Text("searching...", style="dim")
            group = Group(header, Text(""), Padding(status, pad=(0, 0, 0, 2)))
            return self.create_panel(group, "FileSearch")

        # If failed, show error
        if self.failed():
            error_text = self.handle_ansi_output(self.output, apply_dim=False)
            group = Group(header, Text(""), Padding(error_text, pad=(0, 0, 0, 2)))
            return self.create_panel(group, "FileSearch")

        # Parse output to determine what we're showing
        output_text = self.output if self.output else ""

        # Format based on output mode
        if output_mode == "count":
            # Show count results with minimal styling
            result_text = Text.from_ansi(output_text)
            result_padded = Padding(result_text, pad=(0, 0, 0, 2))

            group = Group(header, Text(""), result_padded)
            return self.create_panel(group, "FileSearch ─ Count")

        elif output_mode == "files":
            # Show file list
            result_text = Text.from_ansi(output_text)
            result_padded = Padding(result_text, pad=(0, 0, 0, 2))

            group = Group(header, Text(""), result_padded)
            return self.create_panel(group, "FileSearch ─ Files")

        elif output_mode == "matches":
            # Show matches with syntax highlighting if possible
            # Truncate if output is very long
            max_lines = 50
            lines = output_text.splitlines()

            is_truncated = len(lines) > max_lines
            display_lines = lines[:max_lines] if is_truncated else lines

            result_text = Text.from_ansi('\n'.join(display_lines))

            if is_truncated:
                truncation_msg = Text(f"\n... (showing first {max_lines} of {len(lines)} lines)", style="dim italic")
                result_text.append_text(truncation_msg)

            result_padded = Padding(result_text, pad=(0, 0, 0, 2))

            group = Group(header, Text(""), result_padded)
            return self.create_panel(group, "FileSearch ─ Matches")

        # Fallback for unknown mode
        result_text = Text.from_ansi(output_text)
        result_padded = Padding(result_text, pad=(0, 0, 0, 2))
        group = Group(header, Text(""), result_padded)
        return self.create_panel(group, "FileSearch")


if __name__ == "__main__":
    from rich.console import Console

    console = Console()

    # Test count mode
    args_count = {
        "pattern": "def",
        "file_pattern": "*.py",
        "output_mode": "count",
        "case_sensitive": True
    }
    output_count = """Match counts for pattern 'def':

math_operations.py: 6 matches

Total: 6 matches in 1 file"""

    panel = FileSearchToolPanel(args_count, output_count, width=100)
    console.print(panel.display())

    # Test files mode
    args_files = {
        "pattern": "import",
        "file_pattern": "**/*.py",
        "output_mode": "files",
        "case_sensitive": False
    }
    output_files = """Files matching pattern 'import':

orchestral/tools/base.py
orchestral/agent/agent.py
orchestral/llm/client.py"""

    panel = FileSearchToolPanel(args_files, output_files, width=100)
    console.print(panel.display())

    # Test matches mode
    args_matches = {
        "pattern": "def\\s+\\w+\\(",
        "file_pattern": "*.py",
        "output_mode": "matches",
        "case_sensitive": True
    }
    output_matches = """Matches for pattern 'def\\s+\\w+\\(':

math_operations.py:1: def add(a, b):
math_operations.py:11: def subtract(a, b):
math_operations.py:21: def multiply(a, b):
math_operations.py:31: def divide(a, b):
math_operations.py:44: def power(a, b):
math_operations.py:54: def modulo(a, b):"""

    panel = FileSearchToolPanel(args_matches, output_matches, width=100)
    console.print(panel.display())

    # Test pending state
    panel_pending = FileSearchToolPanel(args_count, None, width=100, is_streaming=True)
    console.print(panel_pending.display())

    # Test failed state
    error_output = "Error: Invalid Regex Pattern\nReason: Failed to compile regex"
    panel_failed = FileSearchToolPanel(args_count, error_output, width=100, is_failed=True)
    console.print(panel_failed.display())
