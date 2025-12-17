import subprocess
import select
import time
import os
from typing import Optional
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField


class RunCommandTool(BaseTool):
    """Execute shell commands with optional persistent session support."""

    # Runtime fields - provided by LLM
    command: str | None = RuntimeField(description="The shell command to execute")
    timeout: int | None = RuntimeField(default=None, description="Optional timeout in seconds")

    # State fields - internal configuration
    base_directory: str = StateField(default="./", description="Working directory for commands")
    verbose: bool = StateField(default=False, description="Enable verbose output")
    persistent: bool = StateField(default=False, description="Run in a persistent shell session")

    def _setup(self):
        """Initialize the tool and start persistent shell if needed."""
        self.base_directory = os.path.abspath(self.base_directory)
        if not os.path.exists(self.base_directory):
            raise ValueError(f"Base directory does not exist: {self.base_directory}")

        # Initialize shell process as private attribute (not a Pydantic field)
        self._shell_process: Optional[subprocess.Popen] = None

        # Start persistent shell if enabled
        if self.persistent:
            self._start_persistent_shell()

    def _run(self) -> str:
        """Execute the shell command and return structured output."""
        if self.command is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Command parameter is required",
                suggestion="Provide a valid shell command"
            )

        try:
            if self.persistent:
                result = self._run_persistent(self.command, self.timeout)
            else:
                result = self._run_once(self.command, self.timeout)

            # If result is None or empty, return a generic message
            if not result:
                return self.format_error(
                    error="Empty Output",
                    reason="Command executed but produced no output",
                    suggestion="Try running a different command or adding logging"
                )

            return result

        except Exception as e:
            return self.format_error(
                error="Execution Error",
                reason=str(e),
                suggestion="Ensure the command is correctly formatted and the system is stable"
            )

    def _run_once(self, command: str, timeout: Optional[int] = None) -> str:
        """Execute a single command in an isolated process."""
        try:
            # Ensure we're in the base directory
            full_command = f'cd {self.base_directory} && {command}'

            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return self._format_command_result(command, result.stdout, result.stderr, result.returncode)

        except subprocess.TimeoutExpired:
            return self.format_error(
                error="Command Timeout",
                reason=f"Command exceeded timeout of {timeout} seconds",
                suggestion="Try increasing the timeout or optimizing the command"
            )

        except Exception as e:
            return self.format_error(
                error="Execution Error",
                reason=str(e),
                suggestion="Ensure the command is correctly formatted"
            )

    def _start_persistent_shell(self):
        """Start a persistent shell session."""
        if self._shell_process:
            return  # Already running

        # Set environment for unbuffered output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'  # Force Python to be unbuffered
        env['PYTHONIOENCODING'] = 'utf-8'  # Ensure UTF-8 encoding

        self._shell_process = subprocess.Popen(
            ["bash", "--noprofile", "--norc"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            env=env
        )

        # Ensure stdout and stderr are non-blocking
        os.set_blocking(self._shell_process.stdout.fileno(), False)
        os.set_blocking(self._shell_process.stderr.fileno(), False)

        # Change to base directory (simple initialization, no output capture needed)
        self._shell_process.stdin.write(f'cd {self.base_directory}\n')
        self._shell_process.stdin.flush()
        time.sleep(0.1)  # Give it a moment to execute

    def _run_persistent(self, command: str, timeout: Optional[int] = None) -> str:
        """Execute a command in the persistent shell session."""
        if not self._shell_process or self._shell_process.poll() is not None:
            # Shell is dead or not initialized, restart it
            self._start_persistent_shell()
            if not self._shell_process:
                return self.format_error(
                    error="Persistent Shell Error",
                    reason="Failed to start persistent shell",
                    suggestion="Check system resources and permissions"
                )

        try:
            # Append marker to detect output completion
            self._shell_process.stdin.write(command + "\n")
            self._shell_process.stdin.write("echo DONE\n")
            self._shell_process.stdin.flush()

            stdout_output = []
            stderr_output = []
            start_time = time.time()

            while True:
                elapsed_time = time.time() - start_time
                if timeout and elapsed_time > timeout:
                    return self.format_error(
                        error="Command Timeout",
                        reason=f"Command exceeded timeout of {timeout} seconds",
                        suggestion="Try increasing the timeout or optimizing the command"
                    )

                ready_out, _, _ = select.select([self._shell_process.stdout], [], [], 0.1)
                ready_err, _, _ = select.select([self._shell_process.stderr], [], [], 0.1)

                if ready_out:
                    while True:
                        line = self._shell_process.stdout.readline().strip()
                        if not line:
                            break  # Stop if there's no more output
                        if line == "DONE":
                            return self._format_command_result(command, "\n".join(stdout_output), "\n".join(stderr_output), 0)
                        stdout_output.append(line)

                if ready_err:
                    while True:
                        err_line = self._shell_process.stderr.readline().strip()
                        if not err_line:
                            break
                        stderr_output.append(err_line)

                time.sleep(0.05)  # Avoid busy waiting

            return self._format_command_result(command, "\n".join(stdout_output), "\n".join(stderr_output), 0)

        except (BrokenPipeError, OSError) as e:
            # Shell process died, restart it and retry once
            self._shell_process = None
            self._start_persistent_shell()
            if self._shell_process:
                try:
                    return self._run_persistent(command, timeout)
                except Exception:
                    pass  # Fall through to general error

            return self.format_error(
                error="Persistent Shell Error",
                reason=f"Shell process died: {str(e)}",
                suggestion="Shell has been restarted automatically"
            )

        except Exception as e:
            return self.format_error(
                error="Persistent Shell Error",
                reason=str(e),
                suggestion="Check if the shell session is running"
            )

    def close_persistent_shell(self):
        """Close the persistent shell process."""
        if self._shell_process:
            self._shell_process.stdin.write("exit\n")
            self._shell_process.stdin.flush()
            self._shell_process.terminate()
            self._shell_process = None

    def _format_command_result(self, command: str, stdout: str, stderr: str, returncode: int) -> str:
        """Format the result of a command execution."""
        return (
            f"Command: {command}\n"
            f"Return Code: {returncode}\n"
            f"Standard Output:\n{stdout if stdout else 'None'}\n"
            f"Standard Error:\n{stderr if stderr else 'None'}"
        )