# hayagriva/core/groq_generator.py

from groq import Groq
from hayagriva.exceptions import GenerationError


class GroqGenerator:
    """
    Generator backend using Groq API.
    Supports models like "llama3-8b-8192" or "mixtral-8x7b-instruct".
    """

    def __init__(self, api_key: str, model: str = "llama3-8b-8192"):
        if not api_key:
            raise GenerationError("Groq API key is missing.")

        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as exc:
            raise GenerationError(f"Groq generation failed: {exc}") from exc
