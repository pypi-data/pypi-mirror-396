from rich.console import Group
from rich.text import Text
from rich.padding import Padding

from orchestral.ui.rich_components.tools.base import BaseToolPanel
from orchestral.ui.colors import LABEL_COLOR


class DisplayImageToolPanel(BaseToolPanel):
    """
    Tool panel for displaying images in the UI.

    This panel creates a special HTML marker that the frontend will detect
    and replace with an actual <img> element.
    """

    def __init__(self, args, output=None, width=80, is_streaming=False, is_failed=False):
        super().__init__(args, output, width, is_streaming, is_failed)

    def display(self):
        """
        Display the image panel.

        The panel will include a special marker that the frontend can detect
        and replace with an actual image element above the panel.
        """
        image_path = self.args.get("image_path", "(no path!)")

        # Create the image marker that frontend will detect and place ABOVE the panel
        # Using a unique text pattern without emojis: [ORCHESTRAL_IMAGE:path]
        marker_text = Text(f"[ORCHESTRAL_IMAGE:{image_path}]", style="dim")

        # Create label section
        label = Text(" image:", style=LABEL_COLOR)
        path_text = Text(f"  {image_path}")

        # Group everything together - marker goes first so it appears at top
        group = Group(
            marker_text,
            label,
            path_text
        )

        title = "DisplayImage"

        # Use base class helper for panel creation (auto-handles border styling)
        return self.create_panel(group, title)


if __name__ == "__main__":
    from rich.console import Console

    # Test with different states
    console = Console()

    # Pending state
    tool1 = DisplayImageToolPanel(
        args={'image_path': '/workspace/plot.png'},
        output=None,
        width=80,
        is_streaming=True
    )
    console.print(tool1.display())

    # Completed state
    tool2 = DisplayImageToolPanel(
        args={'image_path': '/workspace/chart.png'},
        output="Image displayed to the user successfully.",
        width=80
    )
    console.print(tool2.display())

    # Failed state
    tool3 = DisplayImageToolPanel(
        args={'image_path': '/workspace/missing.png'},
        output="Error: File not found",
        width=80,
        is_failed=True
    )
    console.print(tool3.display())
