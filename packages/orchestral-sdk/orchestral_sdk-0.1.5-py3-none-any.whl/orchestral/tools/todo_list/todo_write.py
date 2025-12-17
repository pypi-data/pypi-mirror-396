import os
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField


class TodoWrite(BaseTool):
    r"""Update the todo list with tasks in markdown format.

    Write your todo list as a simple markdown checklist. Use this for planning,
    tracking progress, and organizing complex tasks.

    IMPORTANT: Before updating, use TodoRead to check the current list if you're
    not certain what's already on it. This tool REPLACES the entire list.

    Markdown Format:
    - [ ] Pending task
    - [*] Task currently in progress (use for ONE task at a time)
    - [x] Completed task

    You can add subtasks, notes, or any other markdown formatting as needed.

    Example:
    todos='''
    ## Current Sprint

    - [x] Review project requirements
    - [*] Implement authentication
        - [x] Set up JWT tokens
        - [ ] Add refresh token logic
    - [ ] Write integration tests
    - [ ] Deploy to staging

    Note: Auth implementation is blocked on API key from DevOps
    '''

    Tips:
    - Keep tasks actionable and specific
    - Mark ONE task as [*] (in progress) to show current focus
    - Add context/notes inline when helpful
    - Use subtasks to break down complex work
    - Cross off tasks [x] as you complete them
    """

    todos: str | None = RuntimeField(
        description="Complete todo list in markdown format. Use [ ] for pending, [*] for in progress, [x] for completed."
    )
    conversation_id: str = StateField(default="default", description="Conversation identifier")
    initial_todos: str | None = StateField(
        default=None,
        description="Optional initial todos to populate on first write"
    )

    def _run(self) -> str:
        """Write the complete todo list, replacing any existing list."""
        filepath = self._get_todo_file()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Use provided todos or fall back to initial_todos
        content = self.todos
        if content is None and self.initial_todos is not None:
            content = self.initial_todos

        if content is None:
            return "Error: No todos provided"

        # Write the todos to file
        with open(filepath, 'w') as f:
            f.write(content.strip() + '\n')

        # Return simple confirmation
        return "✓ Todo list updated successfully"

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
