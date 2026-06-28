"""Gemini AI provider implementation."""

from backend.config import config
from backend.ai.providers.base_provider import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self):
        try:
            from google import genai
        except ImportError:
            self.client = None
            self.model = None
        else:
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
            self.model = "gemini-2.5-flash"

    def generate(
        self,
        prompt: str,
    ) -> str:
        if self.client is None:
            raise RuntimeError(
                "Gemini provider requested but google-genai is not installed. "
                "Install google-genai or use a different AI provider."
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text


gemini_provider = GeminiProvider()
