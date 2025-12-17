from rich.console import Console, Group
from rich.text import Text
from rich.padding import Padding

import re

def strip_command_header(text: str) -> str:
    '''This pattern is nearly always there for successful commands, so strip it out for cleaner display'''
    pattern = r'^Command: .*\nReturn Code: 0\nOutput:\n?'
    return re.sub(pattern, '', text, flags=re.DOTALL)

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR

class RunCommandToolPanel(BaseToolPanel):
    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display(self):
        command = self.args.get("command", "(no command!)")
        output_text = self.output if self.output else "(no output!)"

        # Strip standard header from command output if present
        output_text = strip_command_header(output_text)

        # Use base class helper for ANSI-aware output with pending state
        output_rich = self.handle_ansi_output(output_text)

        # Decide whether command is short enough for the title
        if len(command) < self.width - 14:
            title = f"RunCommand: `{command}`"

            # Short command goes in title, only show output
            group = Group(
                Text(" output:", style=LABEL_COLOR),
                Padding(output_rich, pad=(0, 0, 0, 3)),
            )
        else:
            title = "RunCommand"

            # Long command goes in body along with output
            group = Group(
                Text(" command:", style=LABEL_COLOR),
                Padding(Text(command), pad=(0, 0, 0, 3)),
                Text(" output:", style=LABEL_COLOR),
                Padding(output_rich, pad=(0, 0, 0, 3)),
            )

        # Use base class helper for panel creation
        return self.create_panel(group, title)


if __name__ == "__main__":
    console = Console()

    # Test short command
    text = 'Command: ls\nReturn Code: 0\nStandard Output:\nexample_file.py  fib.py           prime_numbers.py test_timing.py\n\x1b[34mexample_folder\x1b[m\x1b[m   fibonacci.py     test.txt\nStandard Error:\nNone'
    tool = RunCommandToolPanel(args={'command': 'ls'}, output=text, width=80)
    console.print(Group(tool.display()))

    # Test long command
    text = 'Command: ls -la\nReturn Code: 0\nStandard Output:\nexample_file.py  fib.py           prime_numbers.py test_timing.py\n\x1b[34mexample_folder\x1b[m\x1b[m   fibonacci.py     test.txt\nStandard Error:\nNone'
    tool = RunCommandToolPanel(args={'command': 'python "import numpy as np; print(np.array([1, 2, 3])); print(np.array([4, 5, 6]))"'}, output=text, width=80)
    console.print(Group(tool.display()))