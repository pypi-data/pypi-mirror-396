from rich.console import Console, Group
from rich.text import Text
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR, OUTPUT_DIM_COLOR, PENDING_STYLE


class WebSearchToolPanel(BaseToolPanel):
    """
    Custom panel for WebSearch tool.

    Special handling:
    - Truncates verbose search results to ~7 lines
    - Applies gray/dim styling to de-emphasize large output
    """

    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display(self):
        query = self.args.get("query", "(no query!)")
        output_text = self.output if self.output else "searching..."

        # Truncate output to max 7 lines since search results are verbose
        truncated_output = self.truncate_content(output_text, max_lines=7)

        # Create ANSI-aware text and apply gray styling to de-emphasize
        output_rich = Text.from_ansi(truncated_output)
        output_rich.stylize(OUTPUT_DIM_COLOR)  # Gray out the search results

        # Additional dimming if pending
        if self.is_pending():
            output_rich.stylize(PENDING_STYLE)

        # Decide whether query is short enough for the title
        if len(query) < self.width - 18:
            title = f"WebSearch: \"{query}\""

            # Short query goes in title, only show results
            group = Group(
                Text(" results:", style=LABEL_COLOR),
                Padding(output_rich, pad=(0, 0, 0, 3)),
            )
        else:
            title = "WebSearch"

            # Long query goes in body along with results
            group = Group(
                Text(" query:", style=LABEL_COLOR),
                Padding(Text(query), pad=(0, 0, 0, 3)),
                Text(" results:", style=LABEL_COLOR),
                Padding(output_rich, pad=(0, 0, 0, 3)),
            )

        # Use base class helper for panel creation
        return self.create_panel(group, title)


if __name__ == "__main__":
    console = Console()

    # Test short query
    results = """1. Python Official Documentation - Python.org
Learn about Python, a powerful programming language that lets you work quickly and integrate systems more effectively.

2. Python Tutorial - W3Schools
Start learning Python with interactive examples and exercises.

3. Real Python - Python Tutorials
In-depth Python tutorials for developers of all skill levels.

4. GitHub - Python Projects
Explore thousands of open-source Python projects and repositories.

5. Stack Overflow - Python Questions
Find answers to common Python programming questions."""

    tool = WebSearchToolPanel(args={'query': 'python programming'}, output=results, width=80)
    console.print(tool.display())

    print("\n")

    # Test long query
    tool2 = WebSearchToolPanel(
        args={'query': 'how to implement a machine learning model using tensorflow and keras with GPU acceleration'},
        output=results,
        width=80
    )
    console.print(tool2.display())
