from orchestral.tools.hooks.base import ToolHook, ToolHookResult

from orchestral.tools.hooks.pre.dangerous_command import DangerousCommandHook
from orchestral.tools.hooks.pre.user_approval import UserApprovalHook
from orchestral.tools.hooks.pre.safeguard import SafeguardHook
from orchestral.tools.hooks.pre.confirmation import ConfirmationHook

from orchestral.tools.hooks.post.truncate import TruncateOutputHook
from orchestral.tools.hooks.post.truncate_lines import TruncateLinesHook
from orchestral.tools.hooks.post.summarize import SummarizeHook


__all__ = [
    # Base classes
    "ToolHook",
    "ToolHookResult",

    # Pre-execution hooks
    "DangerousCommandHook",
    "SafeguardHook",
    "UserApprovalHook",
    "ConfirmationHook",

    # Post-execution hooks
    "TruncateOutputHook",
    "TruncateLinesHook",
    "SummarizeHook",
]