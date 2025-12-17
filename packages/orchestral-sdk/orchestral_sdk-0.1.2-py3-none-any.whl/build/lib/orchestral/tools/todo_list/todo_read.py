import os
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import StateField


class TodoRead(BaseTool):
    """Read the current todo list for this conversation.

    Returns the todo list as markdown text. Use this to check what tasks are already
    on the list before making updates.
    """

    conversation_id: str = StateField(default="default", description="Conversation identifier")

    def _run(self) -> str:
        """Read and return the current todo list."""
        filepath = self._get_todo_file()

        if not os.path.exists(filepath):
            return "📝 Todo list is empty"

        with open(filepath, 'r') as f:
            content = f.read().strip()
            return content if content else "📝 Todo list is empty"

    def _get_todo_file(self) -> str:
        """Get the path to the todo file for this conversation.

        Stores todo list inside the conversation directory for the app,
        or in .orchestral/todos/ for standalone/CLI usage.
        """
        # Check if we're in an app context (conversation_id is a timestamp)
        if self.conversation_id != "default" and self.conversation_id.count("-") >= 2:
            # App context: store in app/conversations/{conversation_id}/todos.md
            return os.path.join("app", "conversations", self.conversation_id, "todos.md")
        else:
            # CLI/standalone context: use .orchestral/todos/
            todo_dir = ".orchestral/todos"
            os.makedirs(todo_dir, exist_ok=True)
            return os.path.join(todo_dir, f"todo_{self.conversation_id}.md")
