"""
Mac/Linux persistent terminal implementation using pexpect.

This module provides a clean, testable interface for persistent shell sessions
without any Orchestral dependencies.
"""

import os
import time
from dataclasses import dataclass
from typing import Optional, Callable

try:
    import pexpect
except ImportError:
    raise ImportError(
        "pexpect is required for persistent terminal sessions. "
        "Install it with: pip install pexpect"
    )


@dataclass
class TerminalResult:
    """Result of a terminal command execution."""
    command: str
    output: str
    return_code: int
    execution_time: float


class TerminalSessionError(Exception):
    """Raised when terminal session operations fail."""
    pass


class PersistentTerminal:
    """
    Persistent shell session using pexpect.

    Provides a clean interface for maintaining shell state across multiple
    command executions. No fallbacks, no mocking - it either works or fails clearly.
    """

    def __init__(self):
        self._session: Optional[pexpect.spawn] = None
        self._working_directory: Optional[str] = None
        self._prompt_marker = "ORCHTERM_READY>"

    def start_session(self, working_dir: str) -> None:
        """
        Start a new persistent bash session.

        Args:
            working_dir: Directory to start the session in

        Raises:
            TerminalSessionError: If session cannot be started
        """
        # Clean up any existing session
        if self._session:
            self.close()

        # Validate working directory
        working_dir = os.path.abspath(working_dir)
        if not os.path.exists(working_dir):
            raise TerminalSessionError(f"Working directory does not exist: {working_dir}")

        try:
            # Start bash with no profile/rc files for predictable behavior
            self._session = pexpect.spawn(
                'bash --norc --noprofile',
                cwd=working_dir,
                timeout=30,
                encoding='utf-8',
                codec_errors='replace'
            )

            # Set our custom prompt for reliable detection
            self._session.sendline(f'PS1="{self._prompt_marker} "')

            # Wait for prompt setup to complete
            self._session.expect(self._prompt_marker, timeout=10)
            # Clear buffer after prompt setup
            try:
                self._session.read_nonblocking(size=1000, timeout=0.1)
            except:
                pass

            # Change to working directory
            self._session.sendline(f'cd "{working_dir}"')
            self._session.expect(self._prompt_marker, timeout=10)
            # Clear buffer after cd
            try:
                self._session.read_nonblocking(size=1000, timeout=0.1)
            except:
                pass

            # Send empty line to get clean prompt
            self._session.sendline('')
            self._session.expect(self._prompt_marker, timeout=10)
            # Clear this buffer too
            try:
                self._session.read_nonblocking(size=1000, timeout=0.1)
            except:
                pass

            self._working_directory = working_dir

        except (pexpect.EOF, pexpect.TIMEOUT, pexpect.exceptions.ExceptionPexpect) as e:
            raise TerminalSessionError(f"Failed to start terminal session: {e}")

    def is_alive(self) -> bool:
        """
        Check if the terminal session is alive and responsive.

        Returns:
            True if session is healthy, False otherwise
        """
        if not self._session:
            return False

        if not self._session.isalive():
            return False

        try:
            # Just send a simple echo and check if we get prompt back
            self._session.sendline('')  # Send empty line
            self._session.expect(self._prompt_marker, timeout=3)
            return True
        except (pexpect.EOF, pexpect.TIMEOUT):
            return False

    def execute_command(self, command: str, timeout: int = 30) -> TerminalResult:
        """
        Execute a command in the persistent session.

        Args:
            command: Shell command to execute
            timeout: Maximum time to wait for completion

        Returns:
            TerminalResult with command output and metadata

        Raises:
            TerminalSessionError: If execution fails
        """
        if not self._session:
            raise TerminalSessionError("No active session. Call start_session() first.")

        if not self.is_alive():
            raise TerminalSessionError("Session is not responsive. Restart required.")

        start_time = time.time()

        try:
            # Send command
            self._session.sendline(command)

            # Wait for command completion
            self._session.expect(self._prompt_marker, timeout=timeout)

            # Get command output (everything before the prompt)
            raw_output = self._session.before

            if not raw_output:
                output = ""
            else:
                # Clean up carriage returns and normalize line endings
                cleaned = raw_output.replace('\r\n', '\n').replace('\r', '\n')

                # Filter out the command echo (first line)
                lines = cleaned.split('\n')
                # First line is usually the echoed command, skip it
                if len(lines) > 1 and lines[0].strip() == command.strip():
                    output = '\n'.join(lines[1:]).strip()
                else:
                    # Fallback: just use everything
                    output = cleaned.strip()

            # Get exit code
            self._session.sendline('echo "EXIT_CODE:$?"')
            self._session.expect(self._prompt_marker, timeout=5)

            exit_code_output = self._session.before
            return_code = 0

            # Parse exit code from output
            for line in exit_code_output.split('\n'):
                if line.startswith('EXIT_CODE:'):
                    try:
                        return_code = int(line.split(':')[1])
                    except (ValueError, IndexError):
                        pass
                    break

            execution_time = time.time() - start_time

            return TerminalResult(
                command=command,
                output=output,
                return_code=return_code,
                execution_time=execution_time
            )

        except pexpect.TIMEOUT:
            execution_time = time.time() - start_time
            raise TerminalSessionError(
                f"Command timed out after {timeout}s: {command}\n"
                f"Partial output: {getattr(self._session, 'before', 'None')[:500]}"
            )
        except pexpect.EOF:
            raise TerminalSessionError(f"Session terminated unexpectedly during command: {command}")

    def execute_command_streaming(self, command: str, timeout: int = 30,
                                   callback: Optional[Callable[[str], None]] = None) -> TerminalResult:
        """
        Execute a command with streaming output via callback.

        Args:
            command: Shell command to execute
            timeout: Maximum time to wait for completion
            callback: Optional callback called with output chunks as they arrive

        Returns:
            TerminalResult with complete command output and metadata

        Raises:
            TerminalSessionError: If execution fails
        """
        if not self._session:
            raise TerminalSessionError("No active session. Call start_session() first.")

        if not self.is_alive():
            raise TerminalSessionError("Session is not responsive. Restart required.")

        start_time = time.time()
        accumulated_output = ""

        try:
            # Send command
            self._session.sendline(command)

            # Read output incrementally until we see the prompt
            end_time = time.time() + timeout
            first_line_skipped = False

            while True:
                remaining_timeout = end_time - time.time()
                if remaining_timeout <= 0:
                    raise pexpect.TIMEOUT("Command timed out")

                try:
                    # Use expect with short timeout to get chunks
                    # Match newlines to get output line-by-line for better streaming
                    index = self._session.expect(
                        [self._prompt_marker, '\n'],
                        timeout=min(remaining_timeout, 0.2)  # Short timeout for responsiveness
                    )

                    if index == 0:
                        # Found prompt - command complete
                        # Get any remaining output before prompt
                        if self._session.before:
                            chunk = self._session.before
                            # Filter command echo from first chunk
                            if not first_line_skipped:
                                lines = chunk.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                                if len(lines) > 1 and lines[0].strip() == command.strip():
                                    chunk = '\n'.join(lines[1:])
                                first_line_skipped = True
                            else:
                                chunk = chunk.replace('\r\n', '\n').replace('\r', '\n')

                            if chunk:
                                accumulated_output += chunk
                                if callback:
                                    callback(chunk)
                        break
                    else:
                        # Got output up to a newline - send it
                        chunk = (self._session.before or '') + (self._session.after or '')
                        if chunk:
                            # Filter command echo from first chunk
                            if not first_line_skipped:
                                lines = chunk.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                                if len(lines) > 0 and lines[0].strip() == command.strip():
                                    chunk = '\n'.join(lines[1:])
                                else:
                                    chunk = chunk.replace('\r\n', '\n').replace('\r', '\n')
                                first_line_skipped = True
                            else:
                                chunk = chunk.replace('\r\n', '\n').replace('\r', '\n')

                            if chunk:
                                accumulated_output += chunk
                                if callback:
                                    callback(chunk)

                except pexpect.TIMEOUT:
                    # Timeout waiting for more output - check if there's anything in buffer
                    # If the command completed but we haven't seen the prompt yet, keep waiting
                    continue

            # Get exit code
            self._session.sendline('echo "EXIT_CODE:$?"')
            self._session.expect(self._prompt_marker, timeout=5)

            exit_code_output = self._session.before
            return_code = 0

            # Parse exit code from output
            for line in exit_code_output.split('\n'):
                if line.startswith('EXIT_CODE:'):
                    try:
                        return_code = int(line.split(':')[1])
                    except (ValueError, IndexError):
                        pass
                    break

            execution_time = time.time() - start_time

            return TerminalResult(
                command=command,
                output=accumulated_output.strip(),
                return_code=return_code,
                execution_time=execution_time
            )

        except pexpect.TIMEOUT:
            execution_time = time.time() - start_time
            raise TerminalSessionError(
                f"Command timed out after {timeout}s: {command}\n"
                f"Partial output: {accumulated_output[:500]}"
            )
        except pexpect.EOF:
            raise TerminalSessionError(f"Session terminated unexpectedly during command: {command}")

    def restart_session(self, working_dir: Optional[str] = None) -> None:
        """
        Restart the terminal session.

        Args:
            working_dir: Directory to restart in (uses previous if None)

        Raises:
            TerminalSessionError: If restart fails
        """
        if working_dir is None:
            working_dir = self._working_directory

        if working_dir is None:
            raise TerminalSessionError("No working directory specified for restart")

        # Close existing session
        self.close()

        # Start new session
        self.start_session(working_dir)

    def close(self) -> None:
        """Clean shutdown of the terminal session."""
        if self._session:
            try:
                if self._session.isalive():
                    self._session.sendline('exit')
                    self._session.expect(pexpect.EOF, timeout=5)
            except (pexpect.TIMEOUT, pexpect.EOF):
                pass  # Session already dead or unresponsive
            finally:
                self._session.close()
                self._session = None

    def __del__(self):
        """Ensure session is closed on object destruction."""
        self.close()