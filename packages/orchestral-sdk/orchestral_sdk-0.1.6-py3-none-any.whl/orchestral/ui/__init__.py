"""
Orchestral UI Module

High-level interface for interactive sessions with agents.

Terminal UI Quick Start:
    from orchestral import Agent
    from orchestral.ui import run_interactive_session

    agent = Agent(tools=[...])
    run_interactive_session(agent, streaming=True)

Web UI Quick Start:
    from orchestral import Agent
    from orchestral.ui.web import run_server

    agent = Agent(tools=[...])
    run_server(agent)  # Opens browser automatically
"""

from orchestral.ui.interactive import run_interactive_session
from orchestral.ui.format_context import display_context, CachedContextDisplay
from orchestral.ui.streaming_display import StreamingDisplay

__all__ = [
    'run_interactive_session',
    'display_context',
    'CachedContextDisplay',
    'StreamingDisplay',
]
