from typing import Any

from google import genai

from src.helper.config import settings


class Gemini:
    _client: genai.Client

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    async def __aenter__(self) -> "Gemini":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass
        # await self.client.close()  # or whatever method you use to release your client resources

    async def generate_content(self, content: str) -> str:
        """
        TODO: streamとかいろいろ検証できそう。
        :param content:
        :return:
        """
        response = await self._client.aio.models.generate_content(model="gemini-pro", contents=content)
        return response.text or ""
