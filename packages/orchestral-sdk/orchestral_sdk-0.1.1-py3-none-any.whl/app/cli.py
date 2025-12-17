"""
Command-line interface for Orchestral AI.

This module provides the main entry point for running the Orchestral web app.
"""

import os
import sys
import time
import argparse


def main():
    """Main entry point for the orchestral CLI."""
    parser = argparse.ArgumentParser(
        description="Orchestral AI - Multi-provider LLM agent framework with web interface"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-0",
        help="Default LLM model to use (default: claude-sonnet-4-0)"
    )

    args = parser.parse_args()

    # Import here to avoid slow startup for --help
    from orchestral import Agent
    from orchestral.tools import (
        RunCommandTool, WebSearchTool, RunPythonTool,
        WriteFileTool, ReadFileTool, EditFileTool,
        FileSearchTool, FindFilesTool,
        TodoWrite, TodoRead, DisplayImageTool
    )
    from orchestral.tools.hooks import DangerousCommandHook, UserApprovalHook
    from orchestral.prompts import RICH_UI_SYSTEM_PROMPT
    from orchestral.llm import Claude

    # Get the workspace directory (app/workspace)
    # For installed package, we need to get the package installation directory
    import app
    app_dir = os.path.dirname(os.path.abspath(app.__file__))
    base_directory = os.path.join(app_dir, "workspace")

    # Ensure workspace directory exists
    os.makedirs(base_directory, exist_ok=True)

    print(f"📁 Workspace directory: {base_directory}")

    # Create agent with tools
    tools = [
        RunCommandTool(base_directory=base_directory),
        RunPythonTool(base_directory=base_directory),
        WriteFileTool(base_directory=base_directory),
        ReadFileTool(base_directory=base_directory, show_line_numbers=True),
        EditFileTool(base_directory=base_directory),
        FindFilesTool(base_directory=base_directory),
        FileSearchTool(base_directory=base_directory),
        WebSearchTool(),
        TodoRead(),
        TodoWrite(initial_todos='- [ ] Sample todo item'),
        DisplayImageTool,
    ]

    # Hooks
    hooks = [
        UserApprovalHook(),
        DangerousCommandHook(),
    ]

    # Create agent with RICH_UI_SYSTEM_PROMPT
    system_prompt = f'{RICH_UI_SYSTEM_PROMPT}\n\nThe current date is {time.strftime("%Y-%m-%d")}'
    llm = Claude(model=args.model)
    agent = Agent(
        llm=llm,
        tools=tools,
        tool_hooks=hooks,
        system_prompt=system_prompt
    )

    # Import and run app server
    import app.server as app_server

    print(f"🚀 Starting Orchestral AI on http://{args.host}:{args.port}")
    print(f"🤖 Using model: {args.model}")
    print("\n⚠️  Note: Agents can execute code on your computer by default")
    print("Press Ctrl+C to stop the server\n")

    app_server.run_server(
        agent,
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser
    )


if __name__ == "__main__":
    main()
