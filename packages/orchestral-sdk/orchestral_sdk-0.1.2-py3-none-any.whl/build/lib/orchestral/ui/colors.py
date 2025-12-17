# Role-based colors for messages
ROLE_COLORS = {
    "user": "white",
    "assistant": "turquoise2",
    "system": "bright_magenta"
}

# Panel border colors
TOOL_COLOR = "gold3"
AGENT_COLOR = "turquoise2"  # Same as assistant
FAILED_COLOR = "red3"  # Used for failed tool calls

# Text styling colors
LABEL_COLOR = "turquoise4"  # Used for labels in tool panels (e.g., "command:", "path:")
OUTPUT_DIM_COLOR = "grey50"  # Used for dimmed output text
PENDING_STYLE = "dim"  # Used for pending tool calls

CHILI_RED = "d13523" # Not used yet

# Code syntax highlighting theme
CODE_THEME = "nord-darker"

# Get theme background color (cached to avoid repeated imports)
_CODE_THEME_BACKGROUND = None

def get_code_theme_background():
    """Get the background color for the current code theme."""
    global _CODE_THEME_BACKGROUND
    if _CODE_THEME_BACKGROUND is None:
        try:
            from pygments.styles import get_style_by_name
            style = get_style_by_name(CODE_THEME)
            _CODE_THEME_BACKGROUND = style.background_color
        except Exception:
            # Fallback if theme lookup fails
            _CODE_THEME_BACKGROUND = "#242933"
    return _CODE_THEME_BACKGROUND