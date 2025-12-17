import re
import json

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.text import Text
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR, CODE_THEME


class RunPythonToolPanel(BaseToolPanel):
    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display(self):
        # Metadata line
        call_text = Text()

        # Show timeout if specified and different from default (10)
        timeout = self.args.get("timeout")
        if timeout and timeout != 10:
            call_text.append(" timeout: ", style=LABEL_COLOR)
            call_text.append(f"{timeout}s\n")

        call_text.append(" code:", style=LABEL_COLOR)

        # Get the Python code
        code = self.args.get("code", "(no code!)")

        # Clean up backticks similar to WriteFile
        code = code.replace('```', '```\n```')
        pattern = r"```(?:\s*\n)*```(?:\n|$)"
        code = re.sub(pattern, "", code)

        # Render as Python code block
        md = Markdown(f'```python\n{code}\n```', code_theme=CODE_THEME)
        md_padded = Padding(md, pad=(0, 1, 0, 2))  # (top, right, bottom, left)

        # Build the group
        group_items = [call_text, md_padded]

        # Add output if available
        if self.output and self.output.strip():
            # Try to parse JSON output
            try:
                output_data = json.loads(self.output)
                stdout = output_data.get("stdout", "")
                stderr = output_data.get("stderr", "")
                return_code = output_data.get("return_code", 0)

                # Show stdout if present
                if stdout:
                    output_label = Text("\n output:", style=LABEL_COLOR)
                    output_rich = Text.from_ansi(stdout)
                    output_padded = Padding(output_rich, pad=(0, 0, 0, 3))
                    group_items.extend([output_label, output_padded])

                # Show stderr if present (in red/warning style)
                if stderr:
                    error_label = Text("\n error:", style="red")
                    error_rich = Text.from_ansi(stderr)
                    error_rich.stylize("red")
                    error_padded = Padding(error_rich, pad=(0, 0, 0, 3))
                    group_items.extend([error_label, error_padded])

                # Show return code only if non-zero
                if return_code != 0:
                    rc_label = Text("\n return code:", style=LABEL_COLOR)
                    rc_text = Text(str(return_code), style="red")
                    rc_padded = Padding(rc_text, pad=(0, 0, 0, 3))
                    group_items.extend([rc_label, rc_padded])

            except json.JSONDecodeError:
                # Fallback to raw output if not valid JSON
                output_label = Text("\n output:", style=LABEL_COLOR)
                output_rich = self.handle_ansi_output(self.output)
                output_padded = Padding(output_rich, pad=(0, 0, 0, 3))
                group_items.extend([output_label, output_padded])

        group = Group(*group_items)

        # Use base class helper for panel creation (auto-handles pending dim style)
        return self.create_panel(group, "RunPython")


if __name__ == "__main__":
    console = Console()

    # Test with code only
    code1 = """import numpy as np
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': [10, 20, 30, 40, 50]
})

print("DataFrame:")
print(df)"""

    tool1 = RunPythonToolPanel(
        args={'code': code1},
        output='{"stdout": "DataFrame:\\n   A   B\\n0  1  10\\n1  2  20\\n2  3  30\\n3  4  40\\n4  5  50", "stderr": "", "return_code": 0}',
        width=80
    )
    console.print(tool1.display())

    print("\n")

    # Test with pending (no output)
    tool2 = RunPythonToolPanel(
        args={'code': 'print("Hello, World!")'},
        output=None,
        width=80
    )
    console.print(tool2.display())
