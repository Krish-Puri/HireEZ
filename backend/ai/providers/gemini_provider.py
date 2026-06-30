"""Gemini AI provider implementation."""

import time
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
        max_retries: int = 3,
    ) -> str:
        if self.client is None:
            raise RuntimeError(
                "Gemini provider requested but google-genai is not installed. "
                "Install google-genai or use a different AI provider."
            )

        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)
                # Retry on rate limit (429) and transient errors
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "500" in err_str or "503" in err_str:
                    wait = (attempt + 1) * 5  # 5, 10, 15 seconds
                    time.sleep(wait)
                    continue
                # Non-retryable error
                raise
        raise last_error


gemini_provider = GeminiProvider()
