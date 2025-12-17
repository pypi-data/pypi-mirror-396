"""
Orchestral terminal tool wrapper with multi-platform backend selection.
"""

import importlib
import os
import platform
from typing import Optional

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

# Global registry to preserve terminals across instance recreation
_GLOBAL_TERMINAL_REGISTRY = {}


def _load_backend():
    sysname = platform.system().lower()
    if sysname in ['darwin', 'linux']:
        module = importlib.import_module('.mac_linux', package=__name__.rsplit('.', 1)[0])
    elif sysname in ['windows']:
        module = importlib.import_module('.windows', package=__name__.rsplit('.', 1)[0])
    else:
        raise ValueError(
            f"Platform '{sysname}' not supported. Supported platforms: darwin, linux, windows"
        )
    return module.PersistentTerminal, module.TerminalSessionError


# Resolve classes at import time so type hints work in editors
PersistentTerminal, TerminalSessionError = _load_backend()


class RunCommandTool(BaseTool):
    """
    Execute shell commands with persistent session state.
    """

    command: str = RuntimeField(
        description="The shell command to execute in the persistent session"
    )
    timeout: int = RuntimeField(
        default=30,
        description="Maximum time to wait for command completion in seconds"
    )

    working_directory: str = StateField(
        default="./",
        description="Working directory for the terminal session"
    )
    base_directory: Optional[str] = StateField(
        default=None,
        description="Alias for working_directory for backward compatibility"
    )
    persistent: bool = StateField(
        default=True,
        description="Legacy parameter. Persistence is always enabled"
    )

    def _setup(self):
        if self.base_directory is not None:
            self.working_directory = self.base_directory

        self.working_directory = os.path.abspath(self.working_directory)
        if not os.path.exists(self.working_directory):
            raise ValueError(f"Working directory does not exist: {self.working_directory}")

        tool_key = f"{self.working_directory}:{id(self.__class__)}"

        if tool_key in _GLOBAL_TERMINAL_REGISTRY:
            terminal = _GLOBAL_TERMINAL_REGISTRY[tool_key]
            object.__setattr__(self, '__terminal', terminal)
        else:
            object.__setattr__(self, '__terminal', None)

        self._platform = platform.system().lower()
        if self._platform not in ['darwin', 'linux', 'windows']:
            raise ValueError(
                f"Platform '{self._platform}' not supported. Supported platforms: darwin, linux, windows"
            )

    def _get_or_create_terminal(self) -> PersistentTerminal:
        terminal = getattr(self, '__terminal', None)
        tool_key = f"{self.working_directory}:{id(self.__class__)}"

        if terminal is None and tool_key in _GLOBAL_TERMINAL_REGISTRY:
            terminal = _GLOBAL_TERMINAL_REGISTRY[tool_key]
            object.__setattr__(self, '__terminal', terminal)

        if terminal is None:
            terminal = PersistentTerminal()
            object.__setattr__(self, '__terminal', terminal)
            _GLOBAL_TERMINAL_REGISTRY[tool_key] = terminal

        if not terminal.is_alive():
            try:
                terminal.start_session(self.working_directory)
                _GLOBAL_TERMINAL_REGISTRY[tool_key] = terminal
            except TerminalSessionError as e:
                object.__setattr__(self, '__terminal', None)
                if tool_key in _GLOBAL_TERMINAL_REGISTRY:
                    del _GLOBAL_TERMINAL_REGISTRY[tool_key]
                raise TerminalSessionError(f"Failed to start terminal session: {e}")

        return terminal

    def _run(self) -> str:
        if not self.command:
            raise ValueError("Command is required")

        try:
            terminal = self._get_or_create_terminal()

            # Check if streaming callback is available
            if hasattr(self, '_stream_callback') and self._stream_callback:
                # Use streaming execution
                result = terminal.execute_command_streaming(
                    command=self.command,
                    timeout=self.timeout,
                    callback=self._stream_callback
                )
            else:
                # Use regular execution
                result = terminal.execute_command(
                    command=self.command,
                    timeout=self.timeout
                )

            return self._format_result(result)

        except TerminalSessionError as e:
            try:
                terminal = getattr(self, '__terminal', None)
                if terminal:
                    terminal.restart_session(self.working_directory)

                    # Retry with streaming if callback available
                    if hasattr(self, '_stream_callback') and self._stream_callback:
                        result = terminal.execute_command_streaming(
                            command=self.command,
                            timeout=self.timeout,
                            callback=self._stream_callback
                        )
                    else:
                        result = terminal.execute_command(
                            command=self.command,
                            timeout=self.timeout
                        )

                    return self._format_result(result)
                else:
                    raise
            except TerminalSessionError:
                return self.format_error(
                    error="Terminal Session Failed",
                    reason=str(e),
                    suggestion="Check command syntax and system state. Session restart failed."
                )

        except Exception as e:
            return self.format_error(
                error="Command Execution Error",
                reason=str(e),
                suggestion="Check command syntax and permissions"
            )

    def _format_result(self, result) -> str:
        return (
            f"Command: {result.command}\n"
            f"Return Code: {result.return_code}\n"
            f"Output:\n{result.output if result.output else 'None'}"
        )

    def close_session(self, force=False):
        terminal = getattr(self, '__terminal', None)
        if terminal:
            tool_key = f"{self.working_directory}:{id(self.__class__)}"
            is_managed = tool_key in _GLOBAL_TERMINAL_REGISTRY and _GLOBAL_TERMINAL_REGISTRY[tool_key] is terminal

            if force or not is_managed:
                terminal.close()
                if is_managed:
                    del _GLOBAL_TERMINAL_REGISTRY[tool_key]

            object.__setattr__(self, '__terminal', None)

    def __del__(self):
        self.close_session()
