"""
Rich to HTML Rendering Utilities

Converts Rich panels to HTML for web UI display.
Reuses existing Rich components (AgentPanel, MessagePanel, ToolPanel).
"""

from io import StringIO
from rich.console import Console
from typing import Any
import re

from orchestral.ui.rich_components.agent import AgentPanel
from orchestral.ui.rich_components.message import MessagePanel
from orchestral.context.context import Context
from orchestral.context.message import Message
from orchestral.llm.base.response import Response


def get_friendly_model_name(model_name: str) -> str:
    """
    Convert technical model names to friendly display names.

    Examples:
        'gpt-4o-mini-2024-07-18' -> 'GPT-4o-mini'
        'claude-3-5-haiku-20241022' -> 'Claude Haiku 3.5'
    """
    if not model_name:
        return model_name

    # Mapping of base model names to friendly names
    model_mapping = {
        # OpenAI
        'gpt-4o-mini': 'GPT-4o-mini',
        'gpt-4o': 'GPT-4o',
        'gpt-4.1-mini': 'GPT-4.1-mini',
        'gpt-4.1': 'GPT-4.1',
        'gpt-5-mini': 'GPT-5-mini',
        'gpt-5': 'GPT-5',

        # Anthropic
        'claude-3-5-haiku': 'Claude Haiku 3.5',
        'claude-3-haiku': 'Claude Haiku 3.0',
        'claude-sonnet-4': 'Claude Sonnet 4',
        'claude-3-7-sonnet': 'Claude Sonnet 3.7',
        'claude-opus-4': 'Claude Opus 4',
        'claude-opus-4-1': 'Claude Opus 4.1',

        # Google
        'gemini-2.0-flash-exp': 'Gemini 2.0 Flash',
        'gemini-1.5-pro': 'Gemini 1.5 Pro',
        'gemini-1.5-flash': 'Gemini 1.5 Flash',
        'gemini-1.5-flash-8b': 'Gemini 1.5 Flash-8B',
        'gemini-1.0-pro': 'Gemini 1.0 Pro',
    }

    # Try exact match first
    if model_name in model_mapping:
        return model_mapping[model_name]

    # Strip date suffixes and version codes
    cleaned = model_name
    cleaned = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', cleaned)  # -YYYY-MM-DD
    cleaned = re.sub(r'-\d{8}$', '', cleaned)  # -YYYYMMDD
    cleaned = re.sub(r'-latest$', '', cleaned)  # -latest

    # Try mapping with cleaned name
    if cleaned in model_mapping:
        return model_mapping[cleaned]

    # Fallback: return original
    return model_name


def render_panel_to_html(panel, width: int = 80) -> str:
    """
    Render a Rich panel to HTML.

    Args:
        panel: Rich Panel object (from AgentPanel, MessagePanel, etc.)
        width: Console width for rendering

    Returns:
        str: HTML string with inline styles
    """
    import io

    # Use StringIO to capture output without printing to terminal
    buffer = io.StringIO()
    console = Console(
        file=buffer,
        record=True,
        width=width,
        force_terminal=True,
        force_interactive=False
    )
    console.print(panel)

    # Export to HTML with inline styles
    html = console.export_html(inline_styles=True, code_format="<pre>{code}</pre>")

    # Restore LaTeX placeholders if the panel has a latex_map
    # Placeholders are short format ℒNℒ to avoid truncation in tables
    if hasattr(panel, '_latex_map') and panel._latex_map:
        for placeholder, latex_block in panel._latex_map.items():
            html = html.replace(placeholder, latex_block)

    return html


def render_message_to_html(role: str, content: str, width: int = 80) -> str:
    """
    Render a message (user/system) to HTML using Rich MessagePanel.
    This ensures consistent styling with the terminal UI.

    Args:
        role: Message role ('user' or 'system')
        content: Message content
        width: Display width

    Returns:
        str: HTML string with Rich styling
    """
    # Use Rich MessagePanel for consistent styling
    panel = MessagePanel(role=role, content=content, width=width)
    return render_panel_to_html(panel.display(), width)


def render_agent_text_to_html(text: str, width: int = 80, model_name: str = None) -> str:
    """
    Render streaming agent text to HTML using Rich AgentPanel.
    This ensures consistent styling with the terminal UI.

    Args:
        text: Agent response text
        width: Display width
        model_name: Optional model name to show as subtitle

    Returns:
        str: HTML string with Rich styling
    """
    # Convert to friendly name if provided
    friendly_name = get_friendly_model_name(model_name) if model_name else None

    # Use Rich AgentPanel for consistent styling
    panel = AgentPanel(response_text=text, width=width, subtitle=friendly_name)
    return render_panel_to_html(panel.display(), width)


def render_agent_panel_to_html(content_items: list, width: int = 80, model_name: str = None) -> str:
    """
    Render complete agent panel with text and tools to HTML.

    Args:
        content_items: List of content items (text/tool dicts)
        width: Display width
        model_name: Optional model name to show as subtitle

    Returns:
        str: HTML string
    """
    # Convert to friendly name if provided
    friendly_name = get_friendly_model_name(model_name) if model_name else None

    panel = AgentPanel(content_items=content_items, width=width, subtitle=friendly_name)
    return render_panel_to_html(panel.display(), width)


def render_full_context_to_html(context: Context, width: int = 80) -> str:
    """
    Render entire conversation context to HTML.

    Args:
        context: Conversation context
        width: Display width

    Returns:
        str: HTML string with all messages
    """
    from orchestral.ui.format_context import format_context
    import io

    # Use StringIO to capture output without printing to terminal
    buffer = io.StringIO()
    console = Console(
        file=buffer,
        record=True,
        width=width,
        force_terminal=True,
        force_interactive=False
    )

    formatted_group = format_context(context, width)
    console.print(formatted_group)

    return console.export_html(inline_styles=True, code_format="<pre>{code}</pre>")


if __name__ == "__main__":
    # Test rendering
    print("Testing Rich to HTML rendering...")

    # Test message rendering
    html = render_message_to_html("user", "Hello, world!")
    print("Message HTML length:", len(html))

    # Test agent text rendering
    html = render_agent_text_to_html("I'll help you with that.")
    print("Agent text HTML length:", len(html))

    print("Rendering utilities ready!")
