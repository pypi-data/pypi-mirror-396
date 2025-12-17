"""
System Prompts for Orchestral

Centralized location for system prompts used across demos and applications.
"""

import os

# Get the directory where this file is located
PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_prompt(filename: str) -> str:
    """
    Load a system prompt from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., 'rich_ui_system_prompt.md')

    Returns:
        str: The prompt content
    """
    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, 'r') as f:
        return f.read()


# Convenient pre-loaded prompts
RICH_UI_SYSTEM_PROMPT = load_prompt('rich_ui_system_prompt.md')


__all__ = ['load_prompt', 'RICH_UI_SYSTEM_PROMPT']
