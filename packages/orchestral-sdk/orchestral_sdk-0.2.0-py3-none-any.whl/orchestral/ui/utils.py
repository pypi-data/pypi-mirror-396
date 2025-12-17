from rich.text import Text
import textwrap


def wrap_text(text, width, indent=0):
    """
    Wraps a multi-line string to a specified width with optional indentation.

    Args:
        text (str): The input text to wrap.
        width (int): Maximum line width.
        indent (int): Number of spaces to indent each line.

    Returns:
        str: The wrapped and indented text.
    """
    indent_str = ' ' * indent

    # Process each line separately
    wrapped_lines = [
        textwrap.fill(
            line,
            width=width,
            initial_indent=indent_str,
            subsequent_indent=indent_str
        ) if line.strip() else ''  # Preserve empty lines
        for line in text.splitlines()
    ]

    return '\n' + '\n'.join(wrapped_lines) + '\n' # Add leading and trailing newlines


def wrap_text_rich(text: Text, width: int, indent: int = 0) -> Text:
    """
    Wrap a Rich Text object while preserving ANSI styles.
    """
    indent_str = ' ' * indent
    lines = []

    for line in text.split("\n"):
        if not line.plain.strip():
            lines.append(Text("\n"))  # preserve empty lines
            continue

        current_line = Text(indent_str)
        for word in line.plain.split():
            if len(current_line.plain) + len(word) + 1 > width:
                lines.append(current_line)
                current_line = Text(indent_str)
            # Add the styled slice from the original line
            start_index = line.plain.find(word, len(current_line.plain) - len(indent_str))
            end_index = start_index + len(word)
            current_line.append(line[start_index:end_index])
            current_line.append(" ")
        lines.append(current_line)

    # Combine lines with newlines
    wrapped_text = Text("\n").join(lines)
    return wrapped_text