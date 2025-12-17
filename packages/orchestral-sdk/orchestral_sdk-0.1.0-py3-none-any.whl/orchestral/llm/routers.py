# LLM package - convenient imports for main clients
from orchestral.llm.base.llm import LLM

class CheapLLM(LLM):
    """Instantiate this LLM as you would any other LLM
    We will automatically select the best available cheap model

    Tries providers in order of cost (cheapest first):
    1. Groq (free tier available)
    2. OpenAI GPT-4o-mini
    3. Claude Haiku
    """

    def __new__(cls, **kwargs):
        """Return an instance of the first available cheap LLM"""

        # Try Groq
        try:
            from orchestral.llm.groq.client import Groq
            return Groq(**kwargs)
        except (ImportError, ValueError):
            pass

        # Try GPT
        try:
            from orchestral.llm.openai.client import GPT
            return GPT(model='gpt-4o-mini', **kwargs)
        except (ImportError, ValueError):
            pass

        # Try Claude
        try:
            from orchestral.llm.anthropic.client import Claude
            return Claude(model='claude-3-5-haiku-latest', **kwargs)
        except (ImportError, ValueError):
            pass

        raise ValueError(
            "No cheap LLMs are available. Please install and configure at least one of:\n"
            "  - Groq (GROQ_API_KEY)\n"
            "  - OpenAI GPT (OPENAI_API_KEY)\n"
            "  - Anthropic Claude (ANTHROPIC_API_KEY)"
        )
        

if __name__ == "__main__":
    llm = CheapLLM()
    from orchestral import Agent
    print(f"Using LLM: {llm.__class__.__name__}")
    agent = Agent(llm=llm)
    response = agent.run("Hello, world!")
    print(f"Agent response: {response}")