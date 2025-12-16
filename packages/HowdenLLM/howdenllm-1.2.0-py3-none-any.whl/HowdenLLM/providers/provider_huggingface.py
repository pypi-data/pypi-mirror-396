from HowdenLLM.providers.base_provider import BaseProvider
from dotenv import load_dotenv
import os


class HuggingFaceProvider(BaseProvider):
    provider = "huggingface"

    def __init__(self):
        from huggingface_hub import InferenceClient
        load_dotenv()
        self.client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))

    def complete(self, system: str, prompt: str, model: str, use_web_search_tool: bool) -> str:
        full_prompt = f"[System]: {system}\n[User]: {prompt}\n"
        response = self.client.text_generation(
            model=model,
            prompt=full_prompt,
            max_new_tokens=500,
            temperature=0.0,
        )
        return response