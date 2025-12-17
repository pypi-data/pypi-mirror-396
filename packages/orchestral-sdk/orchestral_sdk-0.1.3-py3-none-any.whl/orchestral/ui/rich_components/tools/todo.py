from rich.console import Console, Group
from rich.text import Text
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR

### NOTE: [x] is replaced by [✓] only in display, but stored as [x] in the actual todo list, and the agent sees it as [x].

def strip_leading_dashes(text: str) -> str:
    """Remove leading '- ' from every line if all non-empty lines start with it."""
    if not text or not text.strip():
        return text

    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]

    # Check if all non-empty lines start with "- "
    if non_empty_lines and all(line.strip().startswith('- ') for line in non_empty_lines):
        # Remove "- " from the start of each line
        stripped_lines = []
        for line in lines:
            if line.strip().startswith('- '):
                # Find where "- " starts and remove it
                stripped = line.replace('- ', '', 1)
                stripped_lines.append(stripped)
            else:
                # Empty line, keep as is
                stripped_lines.append(line)
        return '\n'.join(stripped_lines)

    return text


def colorize_todo_lines(text: str) -> Text:
    """Colorize todo lines based on their status.

    - [✓] Completed tasks: green x
    - [*] Active tasks: entire line in gold
    - [ ] Pending tasks: default color
    """
    if not text or not text.strip():
        return Text(text)

    lines = text.split('\n')
    result = Text()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Active task [*] - entire line in gold
        if '[*]' in stripped:
            result.append(line, style="gold1")
        # Completed task [✓] - green ✓
        elif '[✓]' in stripped:
            # Split around the [✓] to colorize just the ✓
            parts = line.split('[✓]', 1)
            if len(parts) == 2:
                result.append(parts[0] + '[')
                result.append('✓', style="gold1")
                result.append(']' + parts[1])
            else:
                result.append(line)
        # Pending or other
        else:
            result.append(line)

        # Add newline except for last line
        if i < len(lines) - 1:
            result.append('\n')

    return result


def replace_x_with_checkmark(text: str) -> str:
    """Replace occurrences of '[x]' with a checkmark symbol."""
    return text.replace('[x]', '[✓]')


class TodoReadToolPanel(BaseToolPanel):
    """Custom panel for TodoRead - shows the todo list cleanly."""

    def display(self):
        output_text = self.output if self.output else "Todo list is empty"

        # Strip leading dashes if all lines have them
        output_text = strip_leading_dashes(output_text)

        # Colorize todo lines based on status
        if output_text.strip() and output_text != "Todo list is empty":
            output_text = replace_x_with_checkmark(output_text)
            todo_content = colorize_todo_lines(output_text)
        else:
            todo_content = Text(output_text, style="dim italic")

        # Simple display - just the todo list with a label
        group = Group(
            Padding(todo_content, pad=(0, 0, 0, 1)),
        )

        return self.create_panel(group, "TodoRead")


class TodoWriteToolPanel(BaseToolPanel):
    """Custom panel for TodoWrite - shows updated todo list from args, not output."""

    def display(self):
        # Get the actual todos from the tool arguments (what the agent wrote)
        todo_content = self.args.get("todos", "")

        # Strip leading dashes if all lines have them
        if isinstance(todo_content, str):
            todo_content = strip_leading_dashes(todo_content)

        # Render with colors
        if self.is_pending():
            rendered_content = self.handle_ansi_output(todo_content)
        elif todo_content.strip() if isinstance(todo_content, str) else todo_content:
            # Colorize the todo lines
            if isinstance(todo_content, str):
                todo_content = replace_x_with_checkmark(todo_content)
                rendered_content = colorize_todo_lines(todo_content)
            else:
                rendered_content = Text(str(todo_content))
        else:
            rendered_content = Text("(empty)", style="dim italic")

        # Simple display - just show the updated list
        group = Group(
            Padding(rendered_content, pad=(0, 0, 0, 1)),
        )

        return self.create_panel(group, "TodoWrite")


if __name__ == "__main__":
    console = Console()

    # Test TodoRead
    read_output = """- [x] Create a Python module with a function containing a bug
- [*] Write a pytest test to expose the bug
- [ ] Run the test to confirm the bug exists
- [ ] Fix the bug
- [ ] Verify the fix passes the test"""

    tool = TodoReadToolPanel(args={}, output=read_output, width=80)
    console.print(tool.display())
    print()

    # Test TodoWrite
    write_output = """✓ Todo list updated:

- [x] Create a Python module with a function containing a bug
- [*] Write a pytest test to expose the bug
- [ ] Run the test to confirm the bug exists
- [ ] Fix the bug
- [ ] Verify the fix passes the test"""

    tool = TodoWriteToolPanel(
        args={'todos': '- [x] Create...\n- [*] Write...\n...'},
        output=write_output,
        width=80
    )
    console.print(tool.display())
    print()

    # Test pending state
    tool = TodoWriteToolPanel(
        args={'todos': '- [ ] Some task'},
        output=None,
        width=80,
        is_streaming=True
    )
    console.print(tool.display())
