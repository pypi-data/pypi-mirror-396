import re


from rich.console import Console, Group
from rich.panel import Panel
from rich import box
from rich.markdown import Markdown
from rich.padding import Padding

from orchestral.ui.utils import wrap_text
from orchestral.ui.rich_components.tool import ToolPanel
from orchestral.ui.colors import AGENT_COLOR


def strip_code_block_newlines(text):
    """
    Trim leading/trailing blank lines inside triple backtick code blocks.
    """
    pattern = re.compile(r"```(.*?)```", re.DOTALL)

    def replacer(match):
        code = match.group(1)
        # Strip leading/trailing whitespace/newlines
        stripped = code.strip("\n\r ")
        return f"```\n{stripped}\n```"  # Keep neat format with one newline

    return pattern.sub(replacer, text)



class AgentPanel:
    def __init__(self, response_text=None, tool_uses=None, content_items=None, width=80):
        """
        Create an agent panel with optional response text and tool uses, or ordered content items.

        Args:
            response_text (str, optional): Text response from the agent (legacy mode)
            tool_uses (list, optional): List of tool_use dictionaries (legacy mode)
            content_items (list, optional): Ordered list of content items with text and tools
            width (int): Panel width
        """
        # Support both legacy mode and new ordered content mode
        if content_items is not None:
            self.content_items = content_items
            self.legacy_mode = False
        else:
            # Legacy mode compatibility
            self.response_text = response_text
            self.tool_uses = tool_uses or []
            self.legacy_mode = True

        self.width = width

    def _has_latex(self, text):
        """Check if text contains LaTeX delimiters."""
        if not text:
            return False
        return bool(re.search(r'\$\$?[^$]+\$\$?', text))

    def _protect_latex_blocks(self, text):
        """
        Replace LaTeX blocks with placeholders to prevent line-breaking.
        Returns (modified_text, latex_map).
        """
        latex_map = {}
        counter = [0]  # Use list for closure

        def replacer(match):
            placeholder = f"LATEX_BLOCK_{counter[0]}_PLACEHOLDER"
            latex_map[placeholder] = match.group(0)
            counter[0] += 1
            return placeholder

        # Match both $...$ and $$...$$ patterns
        # Use non-greedy matching to handle multiple equations
        pattern = r'\$\$[^$]+\$\$|\$[^$]+\$'
        protected_text = re.sub(pattern, replacer, text)

        return protected_text, latex_map

    def _restore_latex_blocks(self, text, latex_map):
        """Restore LaTeX blocks from placeholders."""
        for placeholder, latex_block in latex_map.items():
            text = text.replace(placeholder, latex_block)
        return text

    def _render_text_as_markdown(self, text_content):
        """Render text content as markdown with consistent styling."""
        if not text_content or not text_content.strip():
            return None

        # If LaTeX detected, protect it from line-breaking
        has_latex = self._has_latex(text_content)
        latex_map = {}
        if has_latex:
            text_content, latex_map = self._protect_latex_blocks(text_content)

        # Render as markdown with nord-darker theme for code blocks
        text_content = text_content.replace('```', '```\n```')
        pattern = r"```(?:\s*\n)*```(?:\n|$)"
        text_content = re.sub(pattern, "", text_content)
        md = Markdown(text_content, code_theme='nord-darker')

        # Add padding to indent the markdown content with newlines above and below
        md_padded = Padding(md, pad=(1, 0, 1, 1))  # (top, right, bottom, left)

        # Note: We can't easily restore LaTeX here because md_padded is a Rich object,
        # not a string. The restoration will happen in the HTML output.
        # Store the map for later use
        if has_latex:
            md_padded._latex_map = latex_map

        return md_padded

    def display(self):
        """Display the agent panel with response text and tool subpanels."""
        content_parts = []

        if self.legacy_mode:
            # Legacy mode: response text followed by all tools
            if self.response_text and self.response_text.strip():
                markdown_content = self._render_text_as_markdown(self.response_text)
                if markdown_content:
                    content_parts.append(markdown_content)

            # Add tool use subpanels
            if self.tool_uses:
                for tool_use in self.tool_uses:
                    tool_name = tool_use.get('name', 'unknown')
                    args = tool_use.get('arguments', {})
                    output = tool_use.get('output', None)  # None = auto-infer pending

                    tool_panel = ToolPanel(
                        tool_name=tool_name,
                        args=args,
                        output=output,
                        width=self.width - 4
                    )
                    content_parts.append(tool_panel.display())

        else:
            # New mode: process content items in order
            for item in self.content_items:
                if item.get('type') == 'text':
                    text_content = item.get('content', '')
                    if text_content and text_content.strip():
                        markdown_content = self._render_text_as_markdown(text_content)
                        if markdown_content:
                            content_parts.append(markdown_content)

                elif item.get('type') == 'tool':
                    tool_name = item.get('name', 'unknown')
                    args = item.get('arguments', {})
                    output = item.get('output', None)  # None = auto-infer pending

                    tool_panel = ToolPanel(
                        tool_name=tool_name,
                        args=args,
                        output=output,
                        width=self.width - 4
                    )
                    content_parts.append(tool_panel.display())

        # If no content, show a simple message
        if not content_parts:
            content_parts.append(wrap_text("...", width=self.width - 4, indent=1))

        # Create the group of content
        group = Group(*content_parts)

        # Detect if content contains LaTeX
        text_to_check = ""
        if self.legacy_mode:
            text_to_check = self.response_text or ""
        else:
            text_to_check = ' '.join(
                item.get('content', '') for item in self.content_items
                if item.get('type') == 'text'
            )

        has_latex = self._has_latex(text_to_check)

        # Use HORIZONTALS box (no side borders) if LaTeX detected
        panel_box = box.HORIZONTALS if has_latex else box.ROUNDED

        # Create the main panel
        panel = Panel(
            group,
            title="Agent",
            title_align="left",
            width=self.width,
            border_style=AGENT_COLOR,
            box=panel_box,
        )

        # Store latex_map on panel for restoration during HTML rendering
        # Collect all latex_maps from content_parts
        all_latex_maps = {}
        for part in content_parts:
            if hasattr(part, '_latex_map'):
                all_latex_maps.update(part._latex_map)

        if all_latex_maps:
            panel._latex_map = all_latex_maps

        return panel


if __name__ == "__main__":
    console = Console()

    # Test 1: Agent with only response text
    agent1 = AgentPanel(
        response_text="I'll help you list the files and then navigate to the folder.",
        width=80
    )
    console.print(agent1.display())
    print()

    # Test 2: Agent with tool uses only
    agent2 = AgentPanel(
        tool_uses=[
            {
                'name': 'runcommand',
                'arguments': {'command': 'ls'},
                'output': 'Command: ls\nReturn Code: 0\nStandard Output:\nexample_folder  test.txt\nStandard Error:\nNone'
            },
            {
                'name': 'runcommand',
                'arguments': {'command': 'cd example_folder'},
                'output': 'Command: cd example_folder\nReturn Code: 0\nStandard Output:\nNone\nStandard Error:\nNone'
            }
        ],
        width=80
    )
    console.print(agent2.display())
    print()

    # Test 3: Agent with both response text and tool uses
    agent3 = AgentPanel(
        response_text="I found the example_folder and navigated into it. Now let me list the contents:",
        tool_uses=[
            {
                'name': 'runcommand',
                'arguments': {'command': 'ls'},
                'output': 'Command: ls\nReturn Code: 0\nStandard Output:\nfile1.py  file2.txt  data.csv\nStandard Error:\nNone'
            }
        ],
        width=80
    )
    console.print(agent3.display())
    print()

    # Test 4: Agent with different tool types
    agent4 = AgentPanel(
        response_text="I'll create a Python script and then run it:",
        tool_uses=[
            {
                'name': 'writefile',
                'arguments': {'path': 'hello.py', 'data': 'print("Hello, World!")'},
                'output': 'File written successfully'
            },
            {
                'name': 'runcommand',
                'arguments': {'command': 'python hello.py'},
                'output': 'Command: python hello.py\nReturn Code: 0\nStandard Output:\nHello, World!\nStandard Error:\nNone'
            }
        ],
        width=80
    )
    console.print(agent4.display())