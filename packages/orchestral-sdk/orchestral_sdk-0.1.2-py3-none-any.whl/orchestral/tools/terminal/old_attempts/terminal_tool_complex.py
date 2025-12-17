import subprocess
import os
import time
import platform
import shutil
from typing import Optional
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

# Try to import pexpect with platform-specific fallbacks
try:
    if platform.system().lower() == "windows":
        import pexpect_win32 as pexpect
    else:
        import pexpect
    PEXPECT_AVAILABLE = True
except ImportError:
    try:
        # Fallback attempt - try the other library
        if platform.system().lower() == "windows":
            import pexpect
        else:
            import pexpect_win32 as pexpect
        PEXPECT_AVAILABLE = True
    except ImportError:
        PEXPECT_AVAILABLE = False
        print(f"Warning: pexpect not available on {platform.system()}. Terminal tool will use one-shot mode only.")


class RunCommandTool(BaseTool):
    """Execute shell commands with intelligent mode selection and interactive prompt handling."""

    # Runtime fields - provided by LLM
    command: str | None = RuntimeField(description="The shell command to execute")
    timeout: int = RuntimeField(default=30, description="Timeout in seconds")
    interactive_responses: dict = RuntimeField(
        default={},
        description="Optional responses to interactive prompts. Format: {'prompt_pattern': 'response'}"
    )

    # State fields - internal configuration
    base_directory: str = StateField(default="./", description="Working directory for commands")
    persistent_mode: bool = StateField(default=True, description="Use persistent shell session by default")
    auto_fallback: bool = StateField(default=True, description="Automatically fallback to one-shot mode on errors")

    def _setup(self):
        """Simple, fast initialization."""
        self.base_directory = os.path.abspath(self.base_directory)
        if not os.path.exists(self.base_directory):
            raise ValueError(f"Base directory does not exist: {self.base_directory}")

        # Lazy initialization - no shell startup here
        self._shell_session: Optional[pexpect.spawn] = None

    def _run(self) -> str:
        """Execute command with intelligent mode selection."""
        if self.command is None:
            return self.format_error(
                error="Missing Parameter",
                reason="Command parameter is required",
                suggestion="Provide a valid shell command"
            )

        try:
            if self._should_use_persistent():
                return self._execute_persistent()
            else:
                return self._execute_oneshot()

        except Exception as e:
            if self.auto_fallback and self.persistent_mode:
                # Try fallback to one-shot
                try:
                    return self._execute_oneshot()
                except Exception as fallback_e:
                    return self.format_error(
                        error="Command Execution Failed",
                        reason=f"Both persistent and one-shot modes failed: {str(e)}, {str(fallback_e)}",
                        suggestion="Check command syntax and system state"
                    )
            else:
                return self.format_error(
                    error="Command Execution Failed",
                    reason=str(e),
                    suggestion="Check command syntax and permissions"
                )

    def _should_use_persistent(self) -> bool:
        """Determine optimal execution mode."""
        # Can't use persistent mode without pexpect
        if not PEXPECT_AVAILABLE:
            return False

        # User explicitly requested persistent mode
        if self.persistent_mode:
            return True

        # Commands that benefit from persistence
        stateful_commands = ['cd', 'export', 'source', 'alias', 'pushd', 'popd']
        if any(cmd in self.command.lower() for cmd in stateful_commands):
            return True

        # Interactive prompts require persistent mode
        if self.interactive_responses:
            return True

        # Default to one-shot for reliability
        return False

    def _execute_oneshot(self) -> str:
        """Execute command using simple subprocess.run."""
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.base_directory
            )

            return self._format_command_result(
                self.command,
                result.stdout,
                result.stderr,
                result.returncode
            )

        except subprocess.TimeoutExpired:
            return self.format_error(
                error="Command Timeout",
                reason=f"Command exceeded timeout of {self.timeout} seconds",
                suggestion="Try increasing the timeout or optimizing the command"
            )

    def _execute_persistent(self) -> str:
        """Execute command using pexpect persistent session."""
        if not PEXPECT_AVAILABLE:
            return self.format_error(
                error="Persistent Mode Unavailable",
                reason="pexpect library not available on this platform",
                suggestion="Use one-shot mode or install pexpect/pexpect-win32"
            )

        if not self._session_healthy():
            self._start_session()

        try:
            return self._send_command()
        except pexpect.EOF:
            # Session died, restart and retry once
            self._start_session()
            return self._send_command()

    def _session_healthy(self) -> bool:
        """Check if persistent session is alive and responsive."""
        if not self._shell_session:
            return False

        if not self._shell_session.isalive():
            return False

        return True

    def _get_shell_command(self) -> str:
        """Get appropriate shell command for the platform."""
        system = platform.system().lower()

        if system == "windows":
            # On Windows, prefer PowerShell for better functionality, fallback to cmd
            if shutil.which("powershell"):
                return "powershell -NoProfile -NoLogo"
            else:
                return "cmd"
        else:
            # On Unix-like systems, prefer bash for consistency
            if shutil.which("bash"):
                return "bash --norc --noprofile"
            elif shutil.which("sh"):
                return "sh"
            else:
                # Fallback to user's shell
                return os.environ.get('SHELL', '/bin/sh')

    def _start_session(self) -> None:
        """Start or restart persistent shell session."""
        if self._shell_session:
            try:
                self._shell_session.close()
            except:
                pass

        # Start new session with enhanced output capture
        env = os.environ.copy()
        env.update({
            'PYTHONUNBUFFERED': '1',
            'PYTHONIOENCODING': 'utf-8',
            'TERM': 'xterm-256color',  # Enable color support
            'COLUMNS': '120',          # Set consistent width
            'LINES': '40'              # Set consistent height
        })

        # Use platform-appropriate shell
        shell_command = self._get_shell_command()
        self._shell_session = pexpect.spawn(
            shell_command,
            cwd=self.base_directory,
            timeout=self.timeout,
            env=env,
            dimensions=(40, 120)  # Set PTY dimensions for consistent formatting
        )

        # Set platform-appropriate prompt for reliable detection
        if platform.system().lower() == "windows":
            # For Windows shells, we need different prompt setup
            if "powershell" in shell_command.lower():
                self._shell_session.sendline('function prompt { "READY> " }')
                self._shell_session.expect('READY> ', timeout=5)
            else:  # cmd
                self._shell_session.sendline('prompt READY$G$S')
                self._shell_session.expect('READY> ', timeout=5)
        else:
            # Unix-like systems (bash, sh, zsh)
            self._shell_session.sendline('PS1="READY> "')
            self._shell_session.expect('READY> ', timeout=5)

        # Set working directory (platform-agnostic) and clear output
        if platform.system().lower() == "windows":
            # Use Windows path format
            win_path = self.base_directory.replace('/', '\\')
            self._shell_session.sendline(f'cd "{win_path}" && echo "DIR_SET"')
        else:
            self._shell_session.sendline(f'cd "{self.base_directory}" && echo "DIR_SET"')

        # Wait for directory change confirmation and clear it
        self._shell_session.expect('DIR_SET', timeout=5)
        self._shell_session.expect('READY> ', timeout=5)

        # Clear any remaining output buffer after initialization
        try:
            self._shell_session.read_nonblocking(size=10000, timeout=0.2)
        except:
            pass  # No remaining output to clear

    def _send_command(self) -> str:
        """Send command to persistent session and handle responses."""
        if not self._shell_session:
            raise Exception("Shell session not initialized")

        # Clear any existing buffer
        try:
            self._shell_session.read_nonblocking(size=1000, timeout=0.1)
        except:
            pass

        # Send the command directly
        self._shell_session.sendline(self.command)

        # Handle interactive prompts if configured
        if self.interactive_responses:
            return self._handle_interactive_command()
        else:
            return self._handle_simple_command()

    def _handle_simple_command(self) -> str:
        """Handle command without interactive prompts."""
        # Wait for command completion (prompt return)
        try:
            self._shell_session.expect('READY> ', timeout=self.timeout)

            # Get the raw output (preserve all formatting)
            raw_output = self._shell_session.before

            # Also try to get any remaining output in the buffer
            try:
                remaining = self._shell_session.read_nonblocking(size=10000, timeout=0.1)
                if isinstance(remaining, bytes):
                    remaining = remaining.decode('utf-8', errors='replace')
                if raw_output:
                    if isinstance(raw_output, bytes):
                        raw_output = raw_output + remaining.encode('utf-8')
                    else:
                        raw_output = str(raw_output) + str(remaining)
                else:
                    raw_output = remaining
            except:
                pass  # No remaining output

            # Decode with full error handling
            if isinstance(raw_output, bytes):
                output = raw_output.decode('utf-8', errors='replace')
            else:
                output = str(raw_output)

            # Clean up ANSI escape sequences and extra whitespace
            import re
            output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)  # Remove ANSI codes
            output = re.sub(r'\r\n', '\n', output)  # Normalize line endings
            output = re.sub(r'\r', '\n', output)  # Handle remaining carriage returns

            # Simple filtering - remove command echo and empty lines
            lines = output.split('\n')
            filtered_lines = []

            for line in lines:
                # Skip the exact command echo
                if line.strip() == self.command.strip():
                    continue

                # Skip setup artifacts
                if line.strip() in [
                    'PS1="READY> "',
                    'READY>',
                    f'cd "{self.base_directory}"',
                    f'cd {self.base_directory}',
                ]:
                    continue

                # Keep all other lines including empty ones in the middle
                filtered_lines.append(line)

            # Remove leading and trailing empty lines but preserve middle ones
            while filtered_lines and not filtered_lines[0].strip():
                filtered_lines.pop(0)
            while filtered_lines and not filtered_lines[-1].strip():
                filtered_lines.pop()

            stdout = '\n'.join(filtered_lines)

        except pexpect.TIMEOUT:
            # Capture partial output even on timeout
            partial_output = self._shell_session.before.decode('utf-8', errors='replace')
            return self.format_error(
                error="Command Timeout",
                reason=f"Command exceeded timeout of {self.timeout} seconds",
                context=f"Partial output: {partial_output[:500]}...",
                suggestion="Try increasing timeout or check if command is waiting for input"
            )

        # Get exit code using a unique marker to avoid confusion
        exit_marker = f"__EXIT_CODE_{int(time.time())}_END__"
        self._shell_session.sendline(f'echo {exit_marker}$?{exit_marker}')
        self._shell_session.expect('READY> ', timeout=5)

        exit_output = self._shell_session.before.decode('utf-8', errors='replace')
        try:
            # Extract exit code between markers
            start_marker = f"{exit_marker}"
            end_marker = f"{exit_marker}"
            if start_marker in exit_output and end_marker in exit_output:
                exit_str = exit_output.split(start_marker)[1].split(end_marker)[0]
                exit_code = int(exit_str.strip())
            else:
                exit_code = 0
        except:
            exit_code = 0

        return self._format_command_result(self.command, stdout, "", exit_code)

    def _handle_interactive_command(self) -> str:
        """Handle command with interactive prompts."""
        all_output = []

        while True:
            try:
                # Wait for either prompt return or interactive prompt
                patterns = ['READY> '] + list(self.interactive_responses.keys())
                index = self._shell_session.expect(patterns, timeout=self.timeout)

                # Capture raw output preserving all formatting
                raw_output = self._shell_session.before
                if isinstance(raw_output, bytes):
                    output = raw_output.decode('utf-8', errors='replace')
                else:
                    output = str(raw_output)

                all_output.append(output)

                if index == 0:  # Got READY> prompt, command completed
                    break
                else:  # Got interactive prompt
                    prompt_pattern = patterns[index]
                    response = self.interactive_responses[prompt_pattern]

                    # Add the prompt and response to output for visibility
                    all_output.append(f"\n[Interactive Prompt: {prompt_pattern}]")
                    all_output.append(f"[Automated Response: {response}]")

                    self._shell_session.sendline(response)

            except pexpect.TIMEOUT:
                partial_output = '\n'.join(all_output)
                return self.format_error(
                    error="Interactive Command Timeout",
                    reason="Command did not complete within timeout",
                    context=f"Partial output: {partial_output[:500]}...",
                    suggestion="Check if command is waiting for input or adjust interactive_responses"
                )

        # Clean up the output by removing command echo if present
        full_output = '\n'.join(all_output)
        lines = full_output.split('\n')
        if len(lines) > 1 and self.command.strip() in lines[0]:
            stdout = '\n'.join(lines[1:]).rstrip()
        else:
            stdout = full_output.rstrip()

        return self._format_command_result(self.command, stdout, "", 0)

    def close_session(self):
        """Close persistent shell session."""
        if self._shell_session:
            try:
                self._shell_session.close()
            except:
                pass
            self._shell_session = None

    def _format_command_result(self, command: str, stdout: str, stderr: str, returncode: int) -> str:
        """Format the result of a command execution."""
        return (
            f"Command: {command}\n"
            f"Return Code: {returncode}\n"
            f"Standard Output:\n{stdout.strip() if stdout else 'None'}\n"
            f"Standard Error:\n{stderr.strip() if stderr else 'None'}"
        )