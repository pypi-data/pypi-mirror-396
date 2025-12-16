from abc import ABC
from dotenv import load_dotenv
import os
from HowdenLLM.providers.base_provider import BaseProvider

class OpenAIProvider(BaseProvider, ABC):
    provider = "openai"

    def __init__(self):
        from openai import OpenAI
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def complete(self, system: str, prompt: str, model: str, use_web_search_tool: bool) -> str:

        if use_web_search_tool:
            tools = [
                { "type": "web_search" }
            ]
        else:
            tools = None

        if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
            response = self.client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                tools=tools,
                max_output_tokens=16000
            )
        else:
            raise Exception(f"Unsupported model: {model}")

        return response.output_text
