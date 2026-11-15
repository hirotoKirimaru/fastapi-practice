from types import TracebackType
from typing import Self

# PEP 810（Python 3.15）の遅延 import。google.genai は import だけで約 0.35 秒かかるが、
# 使うのは生成 API を叩いたときだけなので、アプリの起動時には読み込まない
lazy from google import genai

from src.helper.config import settings


class Gemini:
    _client: genai.Client

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass
        # await self.client.close()  # or whatever method you use to release your client resources

    async def generate_content(self, content: str) -> str:
        """
        TODO: streamとかいろいろ検証できそう。
        :param content:
        :return:
        """
        response = await self._client.aio.models.generate_content(
            model="gemini-pro", contents=content
        )
        return response.text or ""
