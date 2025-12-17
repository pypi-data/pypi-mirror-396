"""
Workspace service for managing base directory and workspace settings.
"""

from typing import Optional
from pathlib import Path


def extract_base_directory_from_tools(tools: list) -> Optional[str]:
    """
    Extract base_directory from the first tool that has one.

    Args:
        tools: List of tool instances

    Returns:
        Base directory path if found, None otherwise
    """
    if not tools:
        return None

    for tool in tools:
        if hasattr(tool, 'base_directory'):
            return tool.base_directory

    return None


def validate_directory(directory: str) -> bool:
    """
    Validate that a directory exists and is accessible.

    Args:
        directory: Directory path to validate

    Returns:
        True if valid and accessible, False otherwise
    """
    if not directory:
        return False

    try:
        path = Path(directory)
        return path.exists() and path.is_dir()
    except Exception:
        return False
