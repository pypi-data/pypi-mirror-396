# hayagriva/core/generator.py

from openai import OpenAI
from hayagriva.exceptions import GenerationError

class OpenAIGenerator:
    """
    Generator backend using OpenAI API.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if not api_key:
            raise GenerationError("OpenAI API key is missing.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True,
            )

            # Streaming tokens
            for chunk in stream:
                if (
                    chunk.choices
                    and chunk.choices[0].delta
                    and chunk.choices[0].delta.content
                ):
                    yield chunk.choices[0].delta.content

        except Exception as exc:
            raise GenerationError(f"Groq generation failed: {exc}") from exc