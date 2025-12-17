from rich.console import Console, Group
from rich.panel import Panel

from orchestral.ui.utils import wrap_text
from orchestral.ui.colors import ROLE_COLORS

class MessagePanel:
    def __init__(self, role, content, width=80):
        self.role = role
        self.content = content
        self.width = width

    def display(self):
        panel = Panel(
            wrap_text(self.content, width=self.width - 4, indent=1),
            title=self.role.capitalize(),
            title_align="left",
            # subtitle="Rich Library",
            width=self.width,
            border_style=ROLE_COLORS.get(self.role, "white")
        )
        return panel

if __name__ == "__main__":
    message1 = MessagePanel(role="system", content="You are a helpful assistant.")
    message2 = MessagePanel(role="user", content="Hello, World!")
    message3 = MessagePanel(role="assistant", content="This is a very long message that exceeds the width limit and should be wrapped properly.")
    console = Console()
    console.print(Group(message1.display(), message2.display(), message3.display()))