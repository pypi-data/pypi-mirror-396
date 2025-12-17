from orchestral import Agent
from orchestral.llm import GPT
from orchestral.context.summarization.prompts import summarization_system_prompt

# NOTE: This is a very basic summarizer implementation.
# In the future, we will improve this, it is meant to act as a placeholder for now.

class Summarizer:
    def __init__(self, llm=None):
        self.agent = Agent(llm=llm, system_prompt=summarization_system_prompt)

    def summarize(self, text):
        # Remove all messages except the system prompt
        self.agent.context.clear()

        response = self.agent.run(f"Summarize the following text:\n\n{text}")
        return response.text