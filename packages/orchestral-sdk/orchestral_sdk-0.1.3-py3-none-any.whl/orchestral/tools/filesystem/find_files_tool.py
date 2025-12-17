import os
from pathlib import Path
from typing import List
from orchestral.tools.filesystem.filesystem_tools import BaseFileTool
from orchestral.tools.base.field_utils import RuntimeField, StateField


class FindFilesTool(BaseFileTool):
    r"""Find files by NAME/EXTENSION using glob patterns (NOT content search).

    This tool finds files by their filename or path pattern, similar to shell 'find' command.
    For searching FILE CONTENTS, use FileSearchTool instead.

    IMPORTANT: Use GLOB patterns (e.g., '*.py'), NOT regex patterns (e.g., '\.py$').

    Common use cases:
    - "Find all Python files" → pattern='*.py'
    - "Find all test files" → pattern='test_*.py'
    - "Find JavaScript files in src" → pattern='*.js', path='src'
    - "Find all TypeScript files recursively" → pattern='**/*.ts'

    Returns file paths sorted by modification time (most recent first).
    """

    # Runtime parameters (provided by LLM)
    pattern: str | None = RuntimeField(description="GLOB pattern (NOT regex) to match filenames. Examples: '*.py' (Python files), 'test_*.js' (test files), '**/*.ts' (TypeScript files recursively)")
    path: str | None = RuntimeField(default=None, description="Optional subdirectory to search within (e.g., 'demos', 'src/components'). Omit to search entire base_directory.")
    exclude_patterns: List[str] | None = RuntimeField(default=None, description="Optional list of glob patterns to exclude (e.g., ['test_*.py', '*.min.js']). Common excludes like node_modules are already excluded by default.")

    # State parameters (configured by user)
    max_results: int = StateField(default=1000, description="Maximum number of files to return before truncation")
    default_exclude_patterns: List[str] = StateField(
        default_factory=lambda: ['.git', '__pycache__', 'node_modules', '*.pyc', 'dist', 'build', '.venv', '*.min.js'],
        description="Default patterns to exclude (combined with exclude_patterns)"
    )

    def _run(self) -> str:
        """Find files matching the glob pattern."""
        # Validate required fields
        if self.pattern is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Pattern parameter is required",
                suggestion="Provide a glob pattern (e.g., '*.py', '**/*.js')"
            )

        # Determine search directory
        if self.path:
            search_dir = os.path.join(self.base_directory, self.path)
            if not os.path.isdir(search_dir):
                return self.format_error(
                    error="Invalid Path",
                    reason=f"Path does not exist or is not a directory: {self.path}",
                    suggestion="Check the path and try again"
                )
        else:
            search_dir = self.base_directory

        # Combine default and user-provided exclude patterns
        all_excludes = list(self.default_exclude_patterns)
        if self.exclude_patterns:
            all_excludes.extend(self.exclude_patterns)

        # Find files matching pattern
        files = self._find_files(self.pattern, all_excludes, search_dir)

        if not files:
            return f"No files found matching pattern: {self.pattern}"

        # Sort by modification time (most recent first)
        files_with_mtime = []
        for file_path in files:
            try:
                mtime = os.path.getmtime(file_path)
                files_with_mtime.append((file_path, mtime))
            except OSError:
                # Skip files we can't stat
                continue

        files_with_mtime.sort(key=lambda x: x[1], reverse=True)
        sorted_files = [f[0] for f in files_with_mtime]

        # Apply max_results limit
        is_truncated = len(sorted_files) > self.max_results
        result_files = sorted_files[:self.max_results]

        # Format output with relative paths (from base_directory for consistency)
        rel_paths = []
        for file_path in result_files:
            rel_path = os.path.relpath(file_path, self.base_directory)
            rel_paths.append(rel_path)

        # Build output
        header = f"Files matching pattern '{self.pattern}':\n"
        if is_truncated:
            header += f"(showing {self.max_results} of {len(sorted_files)} files, sorted by modification time)\n"
        header += "\n"

        output = header + "\n".join(rel_paths)

        # Add summary
        file_plural = "file" if len(result_files) == 1 else "files"
        output += f"\n\nTotal: {len(result_files)} {file_plural}"

        if is_truncated:
            output += f"\n\n[!] Results truncated at {self.max_results}."
            output += "\nRefine your pattern or use exclude_patterns to narrow scope."

        return output

    def _find_files(self, pattern: str, exclude_patterns: List[str], search_dir: str) -> List[str]:
        """Find all files matching the glob pattern, excluding blacklisted patterns.

        Args:
            pattern: Glob pattern (e.g., '*.py', '**/*.js')
            exclude_patterns: Patterns to exclude
            search_dir: Directory to search in

        Returns:
            List of absolute file paths
        """
        base_path = Path(search_dir)

        # Handle both simple patterns (*.py) and recursive (**/*.py)
        if '**' in pattern:
            # Recursive glob
            matches = base_path.glob(pattern)
        else:
            # Non-recursive - search all subdirectories for the pattern
            matches = base_path.rglob(pattern)

        files = []
        for match in matches:
            # Only include files (not directories)
            if not match.is_file():
                continue

            # Check against exclude patterns
            rel_path = str(match.relative_to(base_path))
            if self._should_exclude(rel_path, exclude_patterns):
                continue

            files.append(str(match))

        return files

    def _should_exclude(self, rel_path: str, exclude_patterns: List[str]) -> bool:
        """Check if a file should be excluded based on exclude_patterns.

        Args:
            rel_path: Relative path from base_directory
            exclude_patterns: Patterns to check against

        Returns:
            True if file should be excluded
        """
        for pattern in exclude_patterns:
            # Check if pattern matches any part of the path
            if pattern.startswith('*.'):
                # File extension pattern
                if rel_path.endswith(pattern[1:]):
                    return True
            else:
                # Directory or filename pattern
                if pattern in rel_path.split(os.sep):
                    return True

        return False
