import textwrap

from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from rich.padding import Padding
from rich import box

from orchestral.ui.colors import TOOL_COLOR, LABEL_COLOR, PENDING_STYLE, FAILED_COLOR


class BaseToolPanel:
    """Base class for custom tool panels with shared helper methods."""

    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        """
        Initialize base tool panel.

        Args:
            args (dict): Tool arguments
            output (str): Tool output/response (None or empty indicates pending)
            width (int): Panel width
            is_streaming (bool): Whether tool is currently streaming output
            is_failed (bool): Whether tool execution failed
        """
        self.args = args
        self.output = output
        self.width = width
        self.is_streaming = is_streaming
        self.is_failed = is_failed

    def is_pending(self):
        """Check if tool is still pending (no output yet) or actively streaming."""
        return self.is_streaming or not self.output or not self.output.strip()

    def failed(self):
        """Check if tool execution failed."""
        return self.is_failed

    def create_label_section(self, label, content, content_padding=3, as_text=False):
        """
        Create a labeled section with consistent formatting.

        Args:
            label (str): The label text (e.g., "command:", "path:")
            content: The content to display (str or Text object)
            content_padding (int): Left padding for content
            as_text (bool): If True, wrap content in Text() object

        Returns:
            Group: A Rich Group with label and padded content
        """
        label_text = Text(f" {label}", style=LABEL_COLOR)

        if isinstance(content, str) and as_text:
            content = Text(content)

        padded_content = Padding(content, pad=(0, 0, 0, content_padding))

        return Group(label_text, padded_content)

    def handle_ansi_output(self, text, apply_dim=None):
        """
        Convert text to ANSI-aware Rich Text with optional styling.

        Args:
            text (str): The text to convert (None means pending)
            apply_dim (bool): If True, apply dim style. If None, use is_pending

        Returns:
            Text: Rich Text object with ANSI codes preserved
        """
        # Show "working..." for pending tools (None or empty output)
        if not text or not text.strip():
            display_text = "working..."
        else:
            display_text = text

        output_rich = Text.from_ansi(display_text)

        # Apply dimming if pending
        should_dim = apply_dim if apply_dim is not None else self.is_pending()
        if should_dim:
            output_rich.stylize(PENDING_STYLE)

        return output_rich

    def truncate_content(self, text, max_lines=None, show_truncated_msg=True, wrap_width=None):
        """
        Truncate text content to a maximum number of lines after wrapping.

        Args:
            text (str): The text to truncate
            max_lines (int): Maximum number of lines to keep (after wrapping)
            show_truncated_msg (bool): If True, add "... (truncated)" message
            wrap_width (int): Width to wrap text to before truncating (defaults to panel width - 10)

        Returns:
            str: Truncated text
        """
        if not text or max_lines is None:
            return text

        # Use wrap_width or default to reasonable width based on panel width
        if wrap_width is None:
            wrap_width = self.width - 10  # Account for padding/borders

        # Wrap the text first to get accurate line count
        wrapped_lines = []
        for line in text.splitlines():
            if line.strip():
                # Wrap each paragraph
                wrapped = textwrap.fill(line, width=wrap_width)
                wrapped_lines.extend(wrapped.splitlines())
            else:
                # Preserve empty lines
                wrapped_lines.append('')

        # Now truncate based on wrapped line count
        if len(wrapped_lines) <= max_lines:
            return text

        truncated_lines = wrapped_lines[:max_lines]
        if show_truncated_msg:
            truncated_lines.append(f"... (truncated {len(wrapped_lines) - max_lines} more lines)")

        return '\n'.join(truncated_lines)

    def create_panel(self, group, title, border_style=None, **kwargs):
        """
        Create a Rich Panel with consistent styling.

        Args:
            group: The content to display in the panel
            title (str): Panel title
            border_style (str): Border color/style (defaults based on state)
            **kwargs: Additional Panel arguments

        Returns:
            Panel: Rich Panel object
        """
        # Auto-apply border style based on state (streaming takes priority over failed)
        if border_style is None:
            if self.is_pending():  # Streaming takes priority
                border_style = "dim"
            elif self.failed():
                border_style = FAILED_COLOR
            else:
                border_style = TOOL_COLOR

        panel_kwargs = {
            'title': title,
            'title_align': 'left',
            'width': self.width,
            'border_style': border_style,
            'box': box.ROUNDED,
        }
        panel_kwargs.update(kwargs)

        return Panel(group, **panel_kwargs)

    def display(self):
        """Display the tool panel. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement display()")
