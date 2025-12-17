from pyexpat import model
from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField

class WebSearchTool(BaseTool):
    """Search the web for information. 
    Use only for external search not for information specific to the user or their system.
    Also don't use it unnecessarily, as it can be slow and costly. Don't use it to retrieve information that you know 'off the top of your head'."""

    query: str = RuntimeField(description="The search query")
    # context: str | None = RuntimeField(description="The context for the search")
    search_context_size: str | None = RuntimeField(description="How much context to include, can be 'low', 'medium', or 'high'.", default="low")

    def _setup(self):
        from openai import OpenAI
        import dotenv
        import os

        dotenv.load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def _run(self) -> str:
        response = self.client.responses.create(
            model='gpt-4o-mini',
            tools=[{"type": "web_search_preview",
                    "search_context_size": self.search_context_size,
            }],                                                        # type: ignore
            input=self.query,
            tool_choice={"type": "web_search_preview"}
        )
        return response.output_text