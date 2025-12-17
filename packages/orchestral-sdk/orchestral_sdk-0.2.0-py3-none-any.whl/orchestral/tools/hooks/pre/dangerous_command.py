from orchestral.tools.hooks.base import ToolHook, ToolHookResult


class DangerousCommandHook(ToolHook):
    """
    Hook that blocks potentially dangerous shell commands.

    This hook only applies to the 'runcommand' tool and checks for
    dangerous patterns like 'rm -rf', 'dd if=', etc.

    Example:
        agent = Agent(hooks=[DangerousCommandHook()])
    """

    # Default dangerous patterns to block
    DEFAULT_PATTERNS = [
        'rm -rf /', # extremely dangerous command
        'rm -rf /*',
        'dd if=',
        'mkfs',
        'format',
        '> /dev/',
        ':(){:|:&};:',  # fork bomb
        'cat /etc/passwd', # access sensitive file, good for demo purposes
    ]

    def __init__(self, additional_patterns=None, patterns=None):
        """
        Initialize the dangerous command hook.

        Args:
            additional_patterns: List of additional patterns to block (added to defaults)
            patterns: List of patterns to block (replaces defaults if provided)
        """
        if patterns is not None:
            self.patterns = patterns
        else:
            self.patterns = self.DEFAULT_PATTERNS.copy()
            if additional_patterns:
                self.patterns.extend(additional_patterns)

    def before_call(self, tool_name: str, arguments: dict) -> ToolHookResult:
        """Check if command contains dangerous patterns."""
        # Only apply to runcommand tool
        if tool_name == 'runcommand':
            command = arguments.get('command', '')
        elif tool_name == 'dummyruncommand':
            command = arguments.get('command', '')
        elif tool_name == 'runpython':
            command = arguments.get('code', '')
        else:
            return ToolHookResult(approved=True)

        # Check for dangerous patterns
        for pattern in self.patterns:
            if pattern in command:
                return ToolHookResult(
                    approved=False,
                    error_message=f"Dangerous command pattern blocked: '{pattern}' detected in command"
                )

        return ToolHookResult(approved=True)
