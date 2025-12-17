import os
from typing import Optional, Dict, Any
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField
from orchestral.tools.filesystem.languages import EXT_TO_LANGUAGE
from orchestral.tools.filesystem._read_registry import FILES_READ  # Global fallback


class BaseFileTool(BaseTool):
    """Base class for all filesystem tools with security controls."""

    # State field for base directory - set once during initialization
    base_directory: str = StateField(default=".", description="Base directory for file operations")

    # Optional context reference - injected by Agent for shared state access
    # Using Any to avoid circular import with Context
    agent_context: Optional[Any] = StateField(default=None, description="Agent context for metadata access")

    def _setup(self):
        """Setup base directory and validate it exists."""
        self.base_directory = os.path.abspath(self.base_directory)
        if not os.path.exists(self.base_directory):
            raise ValueError(f"Base directory does not exist: {self.base_directory}")

    def get_safe_path(self, relative_path: str) -> Optional[str]:
        """Ensures that the path is within the allowed base directory."""
        full_path = os.path.abspath(os.path.join(self.base_directory, relative_path))

        # Prevent escaping the base directory
        if not full_path.startswith(self.base_directory):
            return None
        return full_path

    def _get_files_read_registry(self) -> Dict[str, float]:
        """Get the files_read registry, preferring context metadata over global fallback.

        Returns:
            Dictionary mapping absolute file paths to modification timestamps
        """
        # Prefer context metadata if available
        if self.agent_context is not None:
            if "files_read" not in self.agent_context.metadata:
                self.agent_context.metadata["files_read"] = {}
            return self.agent_context.metadata["files_read"]

        # Fallback to global registry for tools without context
        return FILES_READ

    def _mark_file_read(self, path: str, mtime: float):
        """Mark a file as read with its modification time.

        Args:
            path: Absolute path to the file
            mtime: Modification timestamp from os.path.getmtime()
        """
        registry = self._get_files_read_registry()
        registry[path] = mtime

    def _is_file_read(self, path: str) -> bool:
        """Check if a file has been read.

        Args:
            path: Absolute path to the file

        Returns:
            True if file has been read, False otherwise
        """
        registry = self._get_files_read_registry()
        return path in registry

    def _get_file_read_time(self, path: str) -> Optional[float]:
        """Get the timestamp when a file was read.

        Args:
            path: Absolute path to the file

        Returns:
            Modification timestamp when file was read, or None if not read
        """
        registry = self._get_files_read_registry()
        return registry.get(path)


class ReadFileTool(BaseFileTool):
    """Read file contents with line numbers for reference.

    Line numbers (e.g., '42→') help locate sections when editing.
    Numbers are REFERENCE ONLY - NOT part of file content.
    When editing, copy only the text AFTER the arrow (→), not the line numbers."""

    path: str | None = RuntimeField(description="Relative path to the file within the base directory")
    offset: int = RuntimeField(default=0, description="Line number to start reading from (1-indexed, default 0 for start of file)")
    limit: int = RuntimeField(default=100, description="Maximum number of lines to read (default 100)")

    # StateField - configured by developer when creating tool instance
    show_line_numbers: bool = StateField(default=True, description="Whether to show line numbers in output")

    def _run(self) -> str:
        """Read file contents with proper formatting and security checks."""
        # Validate required fields
        if self.path is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Path parameter is required",
                suggestion="Provide a valid file path"
            )

        # Ensure the path is within the allowed directory
        safe_path = self.get_safe_path(self.path)
        if not safe_path:
            return self.format_error(
                error="Access Denied",
                reason="Attempted to access a file outside the allowed directory.",
                context=f"Path: {self.path}",
                suggestion="Provide a valid relative path within the allowed directory."
            )

        # Check if the file extension is blacklisted
        file_extension = os.path.splitext(safe_path)[1].strip('.')
        ext_blacklist = ['pdf', 'h5', 'hdf5', 'csv', 'png', 'jpeg']
        if file_extension in ext_blacklist:
            if file_extension == 'pdf':
                suggestion = "Use a PDF reading tool to read PDF files."
            elif file_extension in ['h5', 'hdf5', 'csv']:
                suggestion = "Write Python code to read this file type."
            elif file_extension in ['png', 'jpeg']:
                suggestion = "You cannot open images with this tool."
            else:
                suggestion = "Use another tool to read this file type."

            return self.format_error(
                error=f"You are not allowed to use `read_file` on {file_extension} files.",
                reason="This file type is not allowed.",
                context=f"Path: {self.path}",
                suggestion=suggestion
            )

        try:
            with open(safe_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Register this file as read with its modification time (for read-before-edit enforcement)
            # Store the modification time AFTER reading to ensure we capture the state we actually read
            mtime = os.path.getmtime(safe_path)
            self._mark_file_read(safe_path, mtime)  # Uses context metadata if available

            return self._format_contents(content, self.path)

        except FileNotFoundError:
            return self.format_error(
                error="File Not Found",
                reason="The specified file does not exist.",
                context=f"Path: {self.path}",
                suggestion="Check if the file exists or provide a valid path."
            )
        except UnicodeDecodeError:
            return self.format_error(
                error="Encoding Error",
                reason="The file is not encoded in UTF-8 and cannot be read.",
                context=f"Path: {self.path}",
                suggestion="Ensure the file is UTF-8 encoded or contact support."
            )

    def _format_contents(self, content: str, path: str) -> str:
        """Format file contents with line numbers and optional slicing."""
        # Split into lines
        lines = content.split('\n')
        total_lines = len(lines)

        # Step 1: Add line numbers FIRST (before slicing)
        # This ensures line numbers always match file position
        if self.show_line_numbers:
            # Calculate padding for line numbers based on total lines
            # (not sliced lines, so numbers align properly)
            max_line_num = total_lines
            padding = len(str(max_line_num))

            # Add line numbers to ALL lines first
            numbered_lines = []
            for i, line in enumerate(lines, 1):  # 1-indexed
                numbered_lines.append(f"{i:>{padding}}→{line}")
        else:
            numbered_lines = lines

        # Step 2: NOW apply offset/limit slicing
        # offset is 1-indexed for user, but we use 0-indexed internally
        start_idx = max(0, self.offset - 1) if self.offset > 0 else 0

        end_idx = start_idx + self.limit
        sliced_lines = numbered_lines[start_idx:end_idx]

        # Check if we're truncating
        is_truncated = end_idx < total_lines

        # Join the sliced lines
        formatted_content = '\n'.join(sliced_lines)

        # Add truncation indicator if needed
        if is_truncated:
            formatted_content += '\n...'

        # Add metadata about slicing if partial read
        actual_start = start_idx + 1  # Convert back to 1-indexed for display
        actual_end = min(start_idx + len(sliced_lines), total_lines)

        if is_truncated or self.offset > 0:
            header = f"File: {path} (lines {actual_start}-{actual_end} of {total_lines})\n"
        else:
            header = f"File: {path} ({total_lines} lines)\n"

        # Get the file extension for syntax highlighting
        _, ext = os.path.splitext(path)
        ext = ext.lstrip(".")

        if ext in EXT_TO_LANGUAGE:
            language = EXT_TO_LANGUAGE.get(ext, "text")
            return f"{header}```{language}\n{formatted_content}\n```"

        return f"{header}{formatted_content}"


class WriteFileTool(BaseFileTool):
    """Write data to a file, creating it if necessary. Overwrites existing content.

    After writing, you can immediately edit the file without reading it first."""

    path: str | None = RuntimeField(description="Relative path to the file within the allowed directory")
    data: str | None = RuntimeField(description="The content to write into the file")

    def _run(self) -> str:
        """Write data to file with proper security checks."""
        # Validate required fields
        if self.path is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Path parameter is required",
                suggestion="Provide a valid file path"
            )

        if self.data is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Data parameter is required",
                suggestion="Provide content to write to the file"
            )

        safe_path = self.get_safe_path(self.path)
        if not safe_path:
            return self.format_error(
                error="Access Denied",
                reason="Attempted to write to a file outside the allowed directory.",
                context=f"Path: {self.path}",
                suggestion="Provide a valid relative path within the allowed directory."
            )

        try:
            # Ensure the parent directory exists
            directory = os.path.dirname(safe_path)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Write to the file using UTF-8 encoding
            # No need to decode - LLM sends properly formatted strings
            with open(safe_path, "w", encoding="utf-8") as file:
                file.write(self.data)

            # Mark the file as read so it can be edited immediately without needing to read it first
            # This makes sense because we know exactly what content we just wrote
            mtime = os.path.getmtime(safe_path)
            self._mark_file_read(safe_path, mtime)

            return f"Success: The file '{self.path}' has been written to {safe_path}."

        except PermissionError:
            return self.format_error(
                error="Permission Denied",
                reason="The tool lacks permission to write to the specified file.",
                context=f"Path: {self.path}",
                suggestion="Ensure you have the necessary write permissions."
            )
        except OSError as e:
            return self.format_error(
                error="File System Error",
                reason=str(e),
                context=f"Path: {self.path}",
                suggestion="Check available disk space and file system integrity."
            )


class ListDirectoryTool(BaseFileTool):
    """Lists the contents of a directory."""

    path: str = RuntimeField(default=".", description="Relative path to the directory to list (defaults to current directory)")

    def _run(self) -> str:
        """List directory contents with file type indicators."""
        safe_path = self.get_safe_path(self.path)
        if not safe_path:
            return self.format_error(
                error="Access Denied",
                reason="Attempted to access a directory outside the allowed directory.",
                context=f"Path: {self.path}",
                suggestion="Provide a valid relative path within the allowed directory."
            )

        try:
            if not os.path.isdir(safe_path):
                return self.format_error(
                    error="Not a Directory",
                    reason="The specified path is not a directory.",
                    context=f"Path: {self.path}",
                    suggestion="Provide a valid directory path."
                )

            items = os.listdir(safe_path)
            if not items:
                return f"Directory '{self.path}' is empty."

            # Sort items and add type indicators
            formatted_items = []
            for item in sorted(items):
                item_path = os.path.join(safe_path, item)
                if os.path.isdir(item_path):
                    formatted_items.append(f"{item}/")
                else:
                    formatted_items.append(item)

            return f"Contents of '{self.path}':\n" + "\n".join(formatted_items)

        except PermissionError:
            return self.format_error(
                error="Permission Denied",
                reason="The tool lacks permission to read the specified directory.",
                context=f"Path: {self.path}",
                suggestion="Ensure you have the necessary read permissions."
            )
        except OSError as e:
            return self.format_error(
                error="File System Error",
                reason=str(e),
                context=f"Path: {self.path}",
                suggestion="Check if the directory exists and is accessible."
            )