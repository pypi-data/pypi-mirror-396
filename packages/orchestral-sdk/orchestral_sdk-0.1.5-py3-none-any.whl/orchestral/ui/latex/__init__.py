"""
LaTeX conversion system for Orchestral Rich panels.

Converts Rich-formatted terminal output (panels, tool outputs, etc.) to LaTeX
using the tcolorbox package for proper box rendering that mimics the terminal UI.
"""

from orchestral.ui.latex.converter import LatexConverter

__all__ = ['LatexConverter']
