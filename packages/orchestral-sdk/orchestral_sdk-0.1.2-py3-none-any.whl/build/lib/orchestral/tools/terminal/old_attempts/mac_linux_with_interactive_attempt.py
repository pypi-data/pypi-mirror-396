"""
Mac/Linux persistent terminal implementation using pexpect.

This module provides a clean, testable interface for persistent shell sessions
without any Orchestral dependencies.
"""

import os
import time
from dataclasses import dataclass
from typing import Optional

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

    def execute_command(self, command: str, timeout: int = 30, waiting_for_input: bool = False) -> TerminalResult:
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

        print(f"DEBUG: Terminal instance ID: {id(self)}, Session ID: {id(self._session)}")
        start_time = time.time()

        try:
            # Send command (or response to waiting prompt)
            self._session.sendline(command)

            # If we were waiting for input, just expect command completion
            if waiting_for_input:
                print(f"DEBUG: In waiting_for_input branch, sending: '{command}'")
                print(f"DEBUG: Session alive: {self._session.isalive()}")

                # We're responding to an interactive prompt - just wait for completion
                self._session.expect(self._prompt_marker, timeout=timeout)
                print("DEBUG: Got prompt marker after interactive response")

                # For interactive responses, get the output but process it specially
                raw_output = self._session.before
                print(f"DEBUG: Raw output after interactive: '{raw_output}'")

                # The output should contain the completed interactive command result
                execution_time = time.time() - start_time

                # Clean up the output - it might contain the input and result
                if raw_output:
                    # Filter out just our input echo, keep the real output
                    lines = raw_output.split('\n')
                    filtered_lines = []

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        # Skip the input echo
                        if line == command.strip():
                            continue
                        filtered_lines.append(line)

                    output = '\n'.join(filtered_lines)
                else:
                    output = ""

                return TerminalResult(
                    command=command,
                    output=output,
                    return_code=0,  # Successfully provided input
                    execution_time=execution_time
                )
            else:
                # Wait for command completion OR interactive prompt
                # Common interactive patterns: questions ending with ?, (y/n), etc.
                interactive_patterns = [
                    r'.*\?\s*$',           # Questions ending with ?
                    r'.*\(y/n\)\s*$',      # (y/n) prompts
                    r'.*\(Y/n\)\s*$',      # (Y/n) prompts
                    r'.*\(yes/no\)\s*$',   # (yes/no) prompts
                    r'.*:\s*$'             # Prompts ending with :
                ]

                patterns = [self._prompt_marker] + interactive_patterns
                index = self._session.expect(patterns, timeout=timeout)
                print(f"DEBUG: Pattern index: {index}, pattern: {patterns[index] if index < len(patterns) else 'UNKNOWN'}")

                if index == 0:
                    # Got command completion - normal flow
                    pass
                else:
                    # Got interactive prompt - return immediately without accessing session state
                    # This preserves the session in the exact state needed for input
                    return TerminalResult(
                        command=command,
                        output="Enter input: ",  # Generic prompt message
                        return_code=-1,  # Special code indicating waiting for input
                        execution_time=time.time() - start_time
                    )

            # Get command output (everything before the prompt)
            raw_output = self._session.before

            if not raw_output:
                output = ""
            else:
                # Clean up carriage returns and normalize line endings
                cleaned = raw_output.replace('\r\n', '\n').replace('\r', '\n')

                # Split into lines
                lines = cleaned.split('\n')

                # Remove setup artifacts and command echo
                filtered_lines = []
                command_found = False

                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        continue

                    # Skip prompt setup artifacts
                    if line.strip().startswith('"') or line.strip().endswith('"'):
                        continue

                    # Skip the command echo (first occurrence of exact command)
                    if not command_found and line.strip() == command.strip():
                        command_found = True
                        continue

                    # This is actual output
                    filtered_lines.append(line)

                # Join output
                output = '\n'.join(filtered_lines)

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