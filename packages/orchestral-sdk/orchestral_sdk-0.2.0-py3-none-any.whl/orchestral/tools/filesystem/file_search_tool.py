import os
import re
from pathlib import Path
from typing import Optional, List
from orchestral.tools.filesystem.filesystem_tools import BaseFileTool
from orchestral.tools.base.field_utils import RuntimeField, StateField


class FileSearchTool(BaseFileTool):
    """Search for regex patterns in FILE CONTENTS (NOT filenames).

    This tool searches the CONTENTS of files for text/code patterns using regex.
    For finding files by NAME/EXTENSION, use FindFilesTool instead.

    Uses Python's re module for regex matching. Token-efficient with built-in result limits
    and truncation to prevent massive outputs from overly broad searches.

    WORKFLOW: For broad searches, use output_mode='count' first to check scope, then output_mode='matches' to view details.

    Output modes:
    - 'count': Shows match counts per file - use this FIRST to check if pattern is too broad
    - 'matches': Shows matching lines with file paths and line numbers - use after confirming reasonable scope
    - 'files': Shows only file paths containing matches - useful for finding which files to read

    Token efficiency tips:
    - Start with output_mode='count' to avoid overwhelming output
    - Use file_pattern to narrow scope (e.g., '*.py' instead of '*')
    - Refine pattern if count shows too many matches (e.g., 'return True' not 'return')
    - Case-insensitive searches match more, so use case_sensitive=True when possible

    FUTURE: Could add ripgrep support for better performance on large codebases (10k+ files).
    For now, pure Python re module keeps dependencies minimal and behavior consistent.
    """

    # Runtime parameters (provided by LLM)
    pattern: str | None = RuntimeField(description="Regex pattern to search for in file CONTENTS (Python re syntax). Example: 'class\\s+\\w+' to find class definitions")
    file_pattern: str = RuntimeField(default="*", description="Glob pattern to filter which files to search (e.g., '*.py', '**/*.js', 'src/**/*.ts')")
    case_sensitive: bool = RuntimeField(default=True, description="Whether pattern matching is case-sensitive")
    output_mode: str = RuntimeField(
        default="count",
        description="Output format: 'count' (match counts per file - START HERE), 'matches' (full line content with context), 'files' (just file paths)"
    )
    max_results: int = StateField(default=100, description="Maximum results to return before truncation")
    max_file_size: int = StateField(default=1_000_000, description="Skip files larger than this (bytes)")
    context_lines: int = StateField(default=0, description="Lines of context to show before/after matches (0 = none)")
    show_line_numbers: bool = StateField(default=True, description="Show line numbers in output")
    exclude_patterns: List[str] = StateField(
        default_factory=lambda: ['.git', '__pycache__', 'node_modules', '*.pyc', 'dist', 'build', '.venv', '*.min.js'],
        description="Glob patterns for files/directories to exclude"
    )

    def _run(self) -> str:
        """Search files for regex pattern matches."""
        # Validate required fields
        if self.pattern is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Pattern parameter is required",
                suggestion="Provide a regex pattern to search for"
            )

        # Validate output_mode
        valid_modes = ['matches', 'files', 'count']
        if self.output_mode not in valid_modes:
            return self.format_error(
                error="Invalid Parameter",
                reason=f"output_mode must be one of: {', '.join(valid_modes)}",
                context=f"Got: {self.output_mode}",
                suggestion=f"Use one of: {', '.join(valid_modes)}"
            )

        try:
            # Compile regex pattern
            regex_flags = 0 if self.case_sensitive else re.IGNORECASE
            compiled_pattern = re.compile(self.pattern, regex_flags)
        except re.error as e:
            return self.format_error(
                error="Invalid Regex Pattern",
                reason=f"Failed to compile regex: {e}",
                context=f"Pattern: {self.pattern}",
                suggestion="Check your regex syntax (Python re module)"
            )

        # Find files matching file_pattern
        files = self._find_files(self.file_pattern)

        if not files:
            return f"No files found matching pattern: {self.file_pattern}"

        # Search files
        results = []
        total_matches = 0
        files_with_matches = 0

        for file_path in files:
            # Check file size
            try:
                if os.path.getsize(file_path) > self.max_file_size:
                    continue
            except OSError:
                continue

            # Search this file
            file_results = self._search_file(file_path, compiled_pattern)

            if file_results:
                files_with_matches += 1
                match_count = len(file_results)
                total_matches += match_count

                # Get relative path for display
                rel_path = os.path.relpath(file_path, self.base_directory)

                if self.output_mode == 'count':
                    plural = "match" if match_count == 1 else "matches"
                    results.append(f"{rel_path}: {match_count} {plural}")

                elif self.output_mode == 'files':
                    results.append(rel_path)

                elif self.output_mode == 'matches':
                    # Format each match with context
                    for line_num, line_content, context_before, context_after in file_results:
                        if self.show_line_numbers:
                            match_line = f"{rel_path}:{line_num}: {line_content}"
                        else:
                            match_line = f"{rel_path}: {line_content}"

                        # Add context lines if configured
                        if self.context_lines > 0:
                            # Context before
                            for ctx_line in context_before:
                                results.append(f"  {ctx_line}")

                        results.append(match_line)

                        if self.context_lines > 0:
                            # Context after
                            for ctx_line in context_after:
                                results.append(f"  {ctx_line}")

                # Check if we've hit max_results
                if len(results) >= self.max_results:
                    break

        # Format output based on mode
        if not results:
            return f"No matches found for pattern: {self.pattern}"

        # Truncation handling
        is_truncated = len(results) >= self.max_results
        output_lines = results[:self.max_results]

        # Build header
        if self.output_mode == 'count':
            header = f"Match counts for pattern '{self.pattern}':\n"
            if is_truncated:
                header += f"(showing first {self.max_results} files of {files_with_matches})\n"
            header += "\n"

        elif self.output_mode == 'files':
            header = f"Files matching pattern '{self.pattern}':\n"
            if is_truncated:
                header += f"(showing first {self.max_results} of {files_with_matches} files)\n"
            header += "\n"

        elif self.output_mode == 'matches':
            header = f"Matches for pattern '{self.pattern}':\n"
            if is_truncated:
                header += f"(showing first {self.max_results} results)\n"
            header += "\n"

        output = header + "\n".join(output_lines)

        # Add summary footer
        if self.output_mode == 'count':
            plural = "match" if total_matches == 1 else "matches"
            file_plural = "file" if files_with_matches == 1 else "files"
            output += f"\n\nTotal: {total_matches} {plural} in {files_with_matches} {file_plural}"

        # Add truncation warning with helpful suggestion
        if is_truncated:
            output += f"\n\n[!] Results truncated at {self.max_results}."
            output += "\nRefine your search pattern or use file_pattern to narrow scope."
            if self.output_mode == 'matches':
                output += "\nTip: Use output_mode='count' first to check scope before viewing all matches."

        return output

    def _find_files(self, pattern: str) -> List[str]:
        """Find all files matching the glob pattern, excluding blacklisted patterns.

        Args:
            pattern: Glob pattern (e.g., '*.py', '**/*.js')

        Returns:
            List of absolute file paths
        """
        base_path = Path(self.base_directory)

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
            if self._should_exclude(rel_path):
                continue

            files.append(str(match))

        return files

    def _should_exclude(self, rel_path: str) -> bool:
        """Check if a file should be excluded based on exclude_patterns.

        Args:
            rel_path: Relative path from base_directory

        Returns:
            True if file should be excluded
        """
        for pattern in self.exclude_patterns:
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

    def _search_file(self, file_path: str, compiled_pattern: re.Pattern) -> List[tuple]:
        """Search a single file for pattern matches.

        Args:
            file_path: Absolute path to file
            compiled_pattern: Compiled regex pattern

        Returns:
            List of tuples: (line_num, line_content, context_before, context_after)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError, OSError):
            # Skip files that can't be read
            return []

        results = []
        for i, line in enumerate(lines, 1):
            # Remove trailing newline for cleaner display
            line_content = line.rstrip('\n')

            if compiled_pattern.search(line_content):
                # Gather context lines if configured
                context_before = []
                context_after = []

                if self.context_lines > 0:
                    # Lines before (max: context_lines)
                    start_ctx = max(0, i - 1 - self.context_lines)
                    for j in range(start_ctx, i - 1):
                        context_before.append(lines[j].rstrip('\n'))

                    # Lines after (max: context_lines)
                    end_ctx = min(len(lines), i + self.context_lines)
                    for j in range(i, end_ctx):
                        context_after.append(lines[j].rstrip('\n'))

                results.append((i, line_content, context_before, context_after))

        return results
