import os
from typing import Optional
from orchestral.tools.filesystem.filesystem_tools import BaseFileTool
from orchestral.tools.base.field_utils import RuntimeField, StateField
from orchestral.tools.filesystem.languages import EXT_TO_LANGUAGE


def normalize_for_matching(text: str) -> str:
    """Normalize text for more forgiving string matching.

    Converts curly quotes to straight quotes and other common variations.
    This helps when copying text from rich text editors or web pages.
    """
    # Replace curly quotes with straight quotes
    replacements = {
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u201a': "'",  # Single low-9 quotation mark
        '\u201b': "'",  # Single high-reversed-9 quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u201e': '"',  # Double low-9 quotation mark
        '\u201f': '"',  # Double high-reversed-9 quotation mark
        '\u2032': "'",  # Prime
        '\u2033': '"',  # Double prime
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def find_match_positions(content: str, search_str: str, normalize: bool = True) -> list[tuple[int, int]]:
    """Find all positions where search_str appears in content.

    Args:
        content: The text to search in
        search_str: The text to search for
        normalize: If True, normalize quotes before matching

    Returns:
        List of (start, end) tuples indicating match positions in the original content
    """
    if normalize:
        normalized_content = normalize_for_matching(content)
        normalized_search = normalize_for_matching(search_str)
    else:
        normalized_content = content
        normalized_search = search_str

    matches = []
    start = 0

    while True:
        pos = normalized_content.find(normalized_search, start)
        if pos == -1:
            break
        matches.append((pos, pos + len(search_str)))
        start = pos + 1

    return matches


class EditFileTool(BaseFileTool):
    """Edit a file by replacing exact string matches. Safer than rewriting entire files - only changes what you specify.

    Read before edit: You must read the file first UNLESS you just wrote or edited it.
    Copy exact text (including all whitespace, newlines, indentation) into old_string.

    ⚠️  DO NOT include line numbers! Line numbers like '42→' are for reference only.
    Copy only the actual text after the arrow (→).

    The tool errors if old_string appears multiple times (ambiguous) or not at all (not found).
    Include enough context in old_string to ensure a unique match.
    Use replace_all=true only to replace ALL occurrences (e.g., renaming a variable).
    """

    path: str | None = RuntimeField(description="Relative path to the file within the base directory")
    old_string: str | None = RuntimeField(description="Exact text to find and replace. Copy from read_file output, excluding line numbers ('42→'). Must match exactly including whitespace and newlines")
    new_string: str | None = RuntimeField(description="Text to replace old_string with. Do NOT include line numbers")
    replace_all: bool = RuntimeField(default=False, description="If true, replace all occurrences. If false (default), error if multiple matches found")

    def _run(self) -> str:
        """Edit file by replacing exact string matches with safety checks."""
        # Validate required fields
        if self.path is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Path parameter is required",
                suggestion="Provide a valid file path"
            )

        if self.old_string is None:
            return self.format_error(
                error="Missing Parameter",
                reason="old_string parameter is required",
                suggestion="Provide the exact text you want to replace"
            )

        if self.new_string is None:
            return self.format_error(
                error="Missing Parameter",
                reason="new_string parameter is required",
                suggestion="Provide the replacement text (use empty string '' if you want to delete)"
            )

        # Security check - ensure path is within allowed directory
        safe_path = self.get_safe_path(self.path)
        if not safe_path:
            return self.format_error(
                error="Access Denied",
                reason="Attempted to access a file outside the allowed directory",
                context=f"Path: {self.path}",
                suggestion="Provide a valid relative path within the allowed directory"
            )

        # Check if file exists
        if not os.path.exists(safe_path):
            return self.format_error(
                error="File Not Found",
                reason="The specified file does not exist",
                context=f"Path: {self.path}",
                suggestion="Check if the file exists or create it first with write_file"
            )

        # Check if it's actually a file (not a directory)
        if not os.path.isfile(safe_path):
            return self.format_error(
                error="Not a File",
                reason="The specified path is not a file",
                context=f"Path: {self.path}",
                suggestion="Provide a path to a file, not a directory"
            )

        # Enforce "read before edit" - check if file has been read
        if not self._is_file_read(safe_path):
            return self.format_error(
                error="File Not Read",
                reason="You must read the file before editing it",
                context=f"Path: {self.path}",
                suggestion="Use read_file to see the current content first, then copy the exact text you want to change into old_string"
            )

        # Check if file has been modified since it was read
        current_mtime = os.path.getmtime(safe_path)
        read_mtime = self._get_file_read_time(safe_path)

        if read_mtime is not None and current_mtime > read_mtime:
            return self.format_error(
                error="File Modified Since Read",
                reason="The file has been modified since you last read it",
                context=f"Path: {self.path}\nRead at: {read_mtime}\nCurrent: {current_mtime}",
                suggestion="Use read_file again to see the current content, then retry your edit with the updated content"
            )

        try:
            # Read the current file contents
            with open(safe_path, "r", encoding="utf-8") as file:
                original_content = file.read()

            # Find all matching positions using normalized matching
            matches = find_match_positions(original_content, self.old_string, normalize=True)
            count = len(matches)

            # Validate match count
            if count == 0:
                return self.format_error(
                    error="String Not Found",
                    reason=f"The old_string does not appear in the file",
                    context=f"Searched for: {self._truncate_for_display(self.old_string)}",
                    suggestion="Check the exact text including whitespace, or read the file first to see its current contents"
                )

            if count > 1 and not self.replace_all:
                return self.format_error(
                    error="Ambiguous Match",
                    reason=f"The old_string appears {count} times in the file",
                    context=f"Searched for: {self._truncate_for_display(self.old_string)}",
                    suggestion="Include more surrounding context to make old_string unique, or use replace_all=true to replace all occurrences"
                )

            # Perform the replacement using position-based approach
            # This preserves the original content while replacing matched sections
            if self.replace_all:
                # Replace all matches from back to front to preserve positions
                new_content = original_content
                for start, end in reversed(matches):
                    new_content = new_content[:start] + self.new_string + new_content[end:]
            else:
                # Replace only the first occurrence
                start, end = matches[0]
                new_content = original_content[:start] + self.new_string + original_content[end:]

            # Write the modified content back
            with open(safe_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Update the file's read timestamp to the new modification time
            # This allows the agent to edit the file again without re-reading it
            # since we know exactly what content we just wrote
            new_mtime = os.path.getmtime(safe_path)
            self._mark_file_read(safe_path, new_mtime)

            # Calculate line numbers for better user feedback
            lines_before = original_content.count('\n') + 1
            lines_after = new_content.count('\n') + 1
            line_diff = lines_after - lines_before

            # Build success message
            if self.replace_all:
                action = f"Replaced {count} occurrence(s)"
            else:
                action = "Replaced 1 occurrence"

            result = f"Success: {action} in '{self.path}'"

            if line_diff != 0:
                result += f"\nFile now has {lines_after} lines ({line_diff:+d} lines)"

            # Show a snippet of what was changed
            result += f"\n\nChanged from:\n{self._format_snippet(self.old_string)}"
            result += f"\n\nTo:\n{self._format_snippet(self.new_string)}"

            return result

        except UnicodeDecodeError:
            return self.format_error(
                error="Encoding Error",
                reason="The file is not encoded in UTF-8 and cannot be read",
                context=f"Path: {self.path}",
                suggestion="Ensure the file is UTF-8 encoded or use a binary file tool"
            )
        except PermissionError:
            return self.format_error(
                error="Permission Denied",
                reason="Insufficient permissions to read or write the file",
                context=f"Path: {self.path}",
                suggestion="Check file permissions"
            )
        except OSError as e:
            return self.format_error(
                error="File System Error",
                reason=str(e),
                context=f"Path: {self.path}",
                suggestion="Check disk space and file system integrity"
            )

    def _truncate_for_display(self, text: str, max_length: int = 100) -> str:
        """Truncate long strings for error messages."""
        if len(text) <= max_length:
            return repr(text)
        return repr(text[:max_length]) + "... (truncated)"

    def _format_snippet(self, text: str, max_lines: int = 10) -> str:
        """Format text snippet for display, truncating if too long."""
        lines = text.split('\n')
        if len(lines) <= max_lines:
            return f"```\n{text}\n```"

        # Show first few and last few lines
        shown = max_lines // 2
        preview_lines = lines[:shown] + [f"... ({len(lines) - max_lines} more lines) ..."] + lines[-shown:]
        return f"```\n{chr(10).join(preview_lines)}\n```"