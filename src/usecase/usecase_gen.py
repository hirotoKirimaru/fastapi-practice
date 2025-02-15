from typing import Any

import google.generativeai as genai

from src.helper.config import settings


class Gemini:
    _genai: Any
    _model: Any

    def __init__(self):
        self._genai = genai.configure(api_key=settings.GOOGLE_API_KEY)
        self._model = genai.GenerativeModel("gemini-pro")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        # await self.client.close()  # or whatever method you use to release your client resources

    async def generate_content(self, content: str) -> str:
        """
        TODO: streamとかいろいろ検証できそう。
        :param content:
        :return:
        """
        return (await self._model.generate_content_async(content)).text
