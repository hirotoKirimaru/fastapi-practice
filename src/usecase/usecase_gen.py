from google import genai

from src.helper.config import settings


class Gemini:
    _client: genai.Client

    def __init__(self):
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)

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
        response = await self._client.aio.models.generate_content(model="gemini-pro", contents=content)
        return response.text or ""
