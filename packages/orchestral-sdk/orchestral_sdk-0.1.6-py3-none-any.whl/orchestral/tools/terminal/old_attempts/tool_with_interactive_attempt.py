"""
Orchestral terminal tool wrapper.

This is a thin interface layer that delegates to the platform-specific
terminal implementation. It handles Orchestral tool protocol while keeping
the core terminal logic separate and testable.
"""

import platform
from typing import Optional

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

from .mac_linux import PersistentTerminal, TerminalSessionError

# Global registry to preserve terminals across instance recreation
# Note: StateFields work for serializable types, but PersistentTerminal requires this approach
_GLOBAL_TERMINAL_REGISTRY = {}


class RunCommandTool(BaseTool):
    """
    Execute shell commands with persistent session state.

    This tool maintains a persistent shell session that preserves state
    across multiple command executions. Commands like 'cd', 'export',
    and 'source' will persist their effects for subsequent commands.
    Use it exactly as you would normally use a terminal shell, for example with
    interactive commands that require user input run the command and then call the tool again with the input value. 

    Features:
    - Persistent shell state across commands
    - Interactive command support with automated responses
    - Complete output capture including formatting
    - Fast session startup and reliable operation
    - Clear error reporting without silent failures

    RETURN CODES:
    - Return Code 0: Command completed successfully
    - Return Code >0: Command failed with error
    - Return Code -1: Command is waiting for interactive input

    INTERACTIVE FLOW:
    When a command prompts for user input, the tool returns with Return Code -1
    and shows the prompt in the output. To continue, call the tool again with
    your response as the command parameter (just the input value, not a new command).

    Example Interactive Flow:
    1. Call: command="read -p 'Enter name: ' name"
       Returns: Return Code -1, Output: "Enter name: "
    2. Call: command="Alice"  # This is the input value, not a new command
       Returns: Return Code 0, completes the read command

    IMPORTANT: When responding to interactive prompts (Return Code -1),
    provide only the input value in the command parameter, not a new shell command.

    """


    # Runtime fields - provided by LLM
    command: str = RuntimeField(
        description="The shell command to execute in the persistent session"
    )
    timeout: int = RuntimeField(
        default=30,
        description="Maximum time to wait for command completion in seconds"
    )

    # State fields - internal configuration
    working_directory: str = StateField(
        default="./",
        description="Working directory for the terminal session"
    )
    base_directory: Optional[str] = StateField(
        default=None,
        description="Alias for working_directory (for backward compatibility)"
    )
    persistent: bool = StateField(
        default=True,
        description="Legacy parameter - persistence is now always enabled"
    )
    waiting_for_input: bool = StateField(
        default=False,
        description="Whether the terminal is waiting for interactive input"
    )

    def _setup(self):
        """
        Initialize the tool.

        Note: The terminal session is created lazily on first use for fast startup.
        """
        import os

        # Handle backward compatibility: if base_directory is provided, use it
        if self.base_directory is not None:
            self.working_directory = self.base_directory

        self.working_directory = os.path.abspath(self.working_directory)

        # Validate working directory exists
        if not os.path.exists(self.working_directory):
            raise ValueError(f"Working directory does not exist: {self.working_directory}")

        # Use global registry to persist terminals across instance recreation
        tool_key = f"{self.working_directory}:{id(self.__class__)}"

        if tool_key in _GLOBAL_TERMINAL_REGISTRY:
            terminal = _GLOBAL_TERMINAL_REGISTRY[tool_key]
            object.__setattr__(self, '__terminal', terminal)
        else:
            object.__setattr__(self, '__terminal', None)

        self._platform = platform.system().lower()

        # Validate platform support
        if self._platform not in ['darwin', 'linux']:
            raise ValueError(
                f"Platform '{self._platform}' not supported. "
                "Currently only Mac (darwin) and Linux are supported."
            )

    def _get_or_create_terminal(self) -> PersistentTerminal:
        """
        Get the terminal instance, creating it if necessary.

        Returns:
            Active PersistentTerminal instance

        Raises:
            TerminalSessionError: If terminal cannot be created or started
        """
        terminal = getattr(self, '__terminal', None)
        tool_key = f"{self.working_directory}:{id(self.__class__)}"

        # If instance attribute is None, check global registry
        if terminal is None and tool_key in _GLOBAL_TERMINAL_REGISTRY:
            terminal = _GLOBAL_TERMINAL_REGISTRY[tool_key]
            object.__setattr__(self, '__terminal', terminal)

        if terminal is None:
            # Create platform-specific terminal
            if self._platform in ['darwin', 'linux']:
                terminal = PersistentTerminal()
                object.__setattr__(self, '__terminal', terminal)
                # Store in global registry for persistence across instances
                _GLOBAL_TERMINAL_REGISTRY[tool_key] = terminal
            else:
                raise TerminalSessionError(f"Unsupported platform: {self._platform}")

        # Ensure session is started and healthy
        if not terminal.is_alive():
            try:
                terminal.start_session(self.working_directory)
                # Update global registry after successful start
                _GLOBAL_TERMINAL_REGISTRY[tool_key] = terminal
            except TerminalSessionError as e:
                # Clear the terminal reference so next attempt creates fresh
                object.__setattr__(self, '__terminal', None)
                # Remove from global registry on failure
                if tool_key in _GLOBAL_TERMINAL_REGISTRY:
                    del _GLOBAL_TERMINAL_REGISTRY[tool_key]
                raise TerminalSessionError(f"Failed to start terminal session: {e}")

        return terminal

    def _run(self) -> str:
        """
        Execute the command in the persistent terminal session.

        Returns:
            Formatted command result string

        Raises:
            TerminalSessionError: If command execution fails
        """
        if not self.command:
            raise ValueError("Command is required")

        try:
            terminal = self._get_or_create_terminal()

            # Pass waiting state to terminal and execute command
            result = terminal.execute_command(
                command=self.command,
                timeout=self.timeout,
                waiting_for_input=self.waiting_for_input
            )

            # Update waiting state based on result
            self.waiting_for_input = (result.return_code == -1)

            # Format result for Orchestral
            result_str = self._format_result(result)
            return result_str

        except TerminalSessionError as e:
            # Terminal session error - try restart once
            try:
                terminal = getattr(self, '__terminal', None)
                if terminal:
                    terminal.restart_session(self.working_directory)
                    # Retry the command once
                    result = terminal.execute_command(
                        command=self.command,
                        timeout=self.timeout,
                        waiting_for_input=self.waiting_for_input
                    )
                    return self._format_result(result)
                else:
                    raise
            except TerminalSessionError:
                # Give up after one restart attempt
                return self.format_error(
                    error="Terminal Session Failed",
                    reason=str(e),
                    suggestion="Check command syntax and system state. Session restart failed."
                )

        except Exception as e:
            # Unexpected error
            return self.format_error(
                error="Command Execution Error",
                reason=str(e),
                suggestion="Check command syntax and permissions"
            )

    def _format_result(self, result) -> str:
        """
        Format terminal result for Orchestral output.

        Args:
            result: TerminalResult instance

        Returns:
            Formatted string representation
        """
        return (
            f"Command: {result.command}\n"
            f"Return Code: {result.return_code}\n"
            f"Standard Output:\n{result.output if result.output else 'None'}\n"
            f"Standard Error:\nNone"
        )

    def close_session(self, force=False):
        """
        Manually close the terminal session.

        Args:
            force: If True, close even if managed by global registry

        This is typically not needed as sessions are managed automatically,
        but can be useful for cleanup in tests or special circumstances.
        """
        terminal = getattr(self, '__terminal', None)
        if terminal:
            # Check if this terminal is managed by global registry
            tool_key = f"{self.working_directory}:{id(self.__class__)}"
            is_managed = tool_key in _GLOBAL_TERMINAL_REGISTRY and _GLOBAL_TERMINAL_REGISTRY[tool_key] is terminal

            if force or not is_managed:
                terminal.close()
                if is_managed:
                    del _GLOBAL_TERMINAL_REGISTRY[tool_key]

            object.__setattr__(self, '__terminal', None)


    def __del__(self):
        """Ensure terminal session is closed on tool destruction."""
        self.close_session()