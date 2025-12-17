import re

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.text import Text
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.tools.filesystem.languages import EXT_TO_LANGUAGE
from orchestral.ui.colors import LABEL_COLOR, CODE_THEME

class ReadFileToolPanel(BaseToolPanel):
    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display_markdown(self):
        # Metadata line
        call_text = Text()
        # call_text.append(" path: ", style=LABEL_COLOR)
        # call_text.append(self.args.get("path", "(no path!)") + "\n")
        call_text.append(" output:", style=LABEL_COLOR)

        # Markdown content
        output = self.output if self.output else '(no content!)'
        md = Markdown(output, code_theme=CODE_THEME)

        # Indent each line of the Markdown by 2 spaces
        md_padded = Padding(md, pad=(0, 0, 0, 2))  # (top, right, bottom, left)

        # Group metadata and indented markdown
        group = Group(
            call_text,
            md_padded,
            # ''
        )
        
        path = self.args.get("path", "(no path!)")
        title = f"ReadFile: {path}"
        # Use base class helper for panel creation (auto-handles pending dim style)
        return self.create_panel(group, title)


    def display_code(self):
        # Metadata line
        call_text = Text()
        # call_text.append(" path: ", style=LABEL_COLOR)
        path = self.args.get("path", "(no path!)")
        # call_text.append(path + "\n")
        call_text.append(" output:", style=LABEL_COLOR)

        # Markdown content
        extension = path.split('.')[-1] if '.' in path else ''
        language = EXT_TO_LANGUAGE.get(extension, '')
        code = self.output if self.output else '(no content!)'
        # Jake's even more galaxy brain solution which replaced my brilliant solution:
        code = code.replace('```', '```\n```')
        # Alex's hacky solution to avoid backtick issues that openai couldn't figure out!
        # code = code.replace('```\n', '```\n```markdown\n')
        # code = code.replace('```python', '```\n```python')
        pattern = r"```(?:\s*\n)*```(?:\n|$)"
        code = re.sub(pattern, "", code)
        md = Markdown(f'```{language}\n{code}\n```', code_theme=CODE_THEME)

        md_padded = Padding(md, pad=(0, 1, 0, 2))  # (top, right, bottom, left)

        # Group metadata and indented markdown
        group = Group(
            call_text,
            md_padded,
            # md
            # ''
        )

        # Use base class helper for panel creation (auto-handles pending dim style)
        title = f"ReadFile: {path}"
        return self.create_panel(group, title)
    
    
    def display(self):
        code_extensions = ['py', 'js', 'ts', 'java', 'c', 'cpp', 'cs', 'rb', 'go', 'rs', 'html', 'css', 'json', 'xml', 'sh', 'bash', 'zsh', 'yaml', 'yml', 'cc', 'cmnd', 'card']
        if self.args.get("path", '.').split('.')[-1] in code_extensions:
            return self.display_code()
        else:
            return self.display_markdown()


if __name__ == "__main__":
    text = """
# This is an H1 header  
**Bold text**, *italic text*, and `inline code`.

- Lists
- Are
- Supported

## This is an H2 header

### This is an H3 header

```python
from rich import print

print("Code blocks too!")
def example():
    return True

if example():
    print("Works!")

# Check out these colors! and this is a really long comment that should wrap around the panel to test the wrapping functionality of the rich library and see how it handles long lines of text
```
"""
    tool = ReadFileToolPanel(args={'path': 'file1.txt'}, output=text, width=80)
    console = Console()
    console.print(Group(tool.display()))

    code = """# This is a Python script
# This is a really long comment that should wrap around the panel to test the wrapping functionality of the rich library and see how it handles long lines of text

print("Hello, World!")
def add(a, b):
    return a + b
if __name__ == "__main__":
    result = add(5, 7)
    print(f"5 + 7 = {result}")
"""

    tool = ReadFileToolPanel(args={'path': 'script.py'}, output=code, width=80)
    console = Console()
    console.print(Group(tool.display()))