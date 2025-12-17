from orchestral.tools.decorator.define_tool import define_tool

@define_tool()
def DisplayImageTool(image_path: str) -> str:
    """
    This tool displays a given image to the user.
    Use this tool when you make plots or figures that the user should see.
    Generally use it whenever you generate images as part of your workflow even if you don't have a question for the user. Transparency is a key part of the orchestral philosophy.
    Args:
        image_path: The file path to the image to be displayed.
    """
    print('Displaying image at:', image_path)
    return f"Image displayed to the user successfully."