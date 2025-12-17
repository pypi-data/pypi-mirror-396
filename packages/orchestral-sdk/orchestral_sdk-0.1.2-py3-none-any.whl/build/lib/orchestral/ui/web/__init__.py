"""
Orchestral Web UI Module

Provides browser-based interface for agent interactions.

Quick Start:
    from orchestral import Agent
    from orchestral.ui.web import run_server

    agent = Agent(tools=[...])
    run_server(agent)
"""

from orchestral.ui.web.server import run_server

__all__ = ['run_server']
