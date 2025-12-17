# This will define a class which displays tool calls and their responses in a Rich panel format.
# It will be similar to the MessagePanel class in message.py but tailored for tool calls and responses.
# Our tools may have different needs for display, such as showing the tool name and arguments differently.
# For example, terminal commands are often short and can be displayed in the title with their output faintly summarized in the panel body,
# On the other hand, file write operations might have long arguments that need to be displayed in the body and may have no output at all.
# So we will define a default behavior but route specific tools to custom display logic which will be written and located in the tools directory.

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from orchestral.ui.utils import wrap_text_rich

# Specific tool display imports
from orchestral.ui.rich_components.tools.runcommand import RunCommandToolPanel
from orchestral.ui.rich_components.tools.writefile import WriteFileToolPanel
from orchestral.ui.rich_components.tools.readfile import ReadFileToolPanel
from orchestral.ui.rich_components.tools.websearch import WebSearchToolPanel
from orchestral.ui.rich_components.tools.runpython import RunPythonToolPanel
from orchestral.ui.rich_components.tools.editfile import EditFileToolPanel
from orchestral.ui.rich_components.tools.filesearch import FileSearchToolPanel
from orchestral.ui.rich_components.tools.code_argument import CodeArgumentToolPanel
from orchestral.ui.rich_components.tools.todo import TodoReadToolPanel, TodoWriteToolPanel
from orchestral.ui.rich_components.tools.display_image import DisplayImageToolPanel
from orchestral.ui.colors import TOOL_COLOR, OUTPUT_DIM_COLOR, PENDING_STYLE, LABEL_COLOR, FAILED_COLOR


class ToolPanel:
    def __init__(self, tool_name, args, output, width=80, is_streaming=False, is_failed=False):
        self.tool_name = tool_name
        self.args = args
        self.output = output
        self.width = width
        self.is_streaming = is_streaming
        self.is_failed = is_failed

    def is_pending(self):
        """Check if tool is still pending (no output yet) or actively streaming."""
        return self.is_streaming or not self.output or not self.output.strip()

    def failed(self):
        """Check if tool execution failed."""
        return self.is_failed

    def default_display(self):
        import json
        from rich.padding import Padding

        args = ', '.join([f'[gold3]{k}[/gold3]="{v}"' for k, v in self.args.items()])
        call_text = f'[light_blue]{self.tool_name}[/light_blue]({args})'

        # Wrap the tool call text with proper indentation
        call_text_wrapped = wrap_text_rich(Text.from_markup(call_text), width=self.width - 6, indent=3)

        # Process output - try to parse as JSON for nice formatting
        if self.is_pending():
            # Pending state
            response_output = Text("working...", style=PENDING_STYLE)
            wrapped_response = wrap_text_rich(response_output, width=self.width - 6, indent=3)
        else:
            # Try to parse as JSON
            try:
                json_data = json.loads(self.output)
                # Successfully parsed JSON - format nicely
                json_lines = []
                for key, value in json_data.items():
                    line = Text()
                    line.append(f"{key}: ", style='bright_black')
                    line.append(str(value), style="white")
                    json_lines.append(line)

                # Combine all lines and wrap
                json_group = Group(*json_lines)
                wrapped_response = Padding(json_group, pad=(0, 0, 0, 3))
            except (json.JSONDecodeError, AttributeError, TypeError):
                # Not JSON or error parsing - display as regular text
                rich_response = Text.from_ansi(self.output if self.output else "")
                rich_response.stylize(OUTPUT_DIM_COLOR)
                wrapped_response = wrap_text_rich(rich_response, width=self.width - 6, indent=3)

        group = Group(
            Text('  tool call:', style=LABEL_COLOR),
            call_text_wrapped,
            Text('\n  response:', style=LABEL_COLOR),
            wrapped_response,
        )

        # Determine border style (streaming takes priority over failed)
        if self.is_pending():
            border_style = "dim"
        elif self.failed():
            border_style = FAILED_COLOR
        else:
            border_style = TOOL_COLOR

        panel = Panel(
            group,
            # title="Tool",
            # title_align="left",
            width=self.width,
            border_style=border_style,
        )
        return panel
    
    def _has_code_argument(self):
        """Check if any argument contains 'code' in its name."""
        return any('code' in arg_name.lower() for arg_name in self.args.keys())

    def display(self):
        # Route to specific tool display logic if available
        tool_display_map = {
            'writefile': WriteFileToolPanel,
            'readfile': ReadFileToolPanel,
            'runcommand': RunCommandToolPanel,
            'websearch': WebSearchToolPanel,
            'runpython': RunPythonToolPanel,
            'editfile': EditFileToolPanel,
            'filesearch': FileSearchToolPanel,
            'todoread': TodoReadToolPanel,
            'todowrite': TodoWriteToolPanel,
            'displayimage': DisplayImageToolPanel,
            # Add more tools here as needed
        }

        # Check for specific tool first
        if self.tool_name in tool_display_map:
            tool_panel = tool_display_map[self.tool_name](
                self.args,
                self.output,
                self.width,
                is_streaming=self.is_streaming,
                is_failed=self.is_failed
            )
            return tool_panel.display()
        # Check if tool has code arguments
        elif self._has_code_argument():
            tool_panel = CodeArgumentToolPanel(
                self.tool_name,
                self.args,
                self.output,
                self.width,
                is_streaming=self.is_streaming,
                is_failed=self.is_failed
            )
            return tool_panel.display()
        # Fall back to default display
        else:
            return self.default_display()


if __name__ == "__main__":
    tool1 = ToolPanel(tool_name="runcommand", args={'command': '-l -a'}, output="file1.txt\nfile2.txt", width=80)
    tool2 = ToolPanel(tool_name="writefile", args={'path': 'file1.py', 'data': 'print("Hello World")'}, output="Hello, World!", width=80)
    tool3 = ToolPanel(tool_name="unknown_tool", args={'param1': 'value1'}, output="Some output from an unknown tool.", width=80)
    console = Console()
    console.print(Group(tool1.display(), tool2.display(), tool3.display()))