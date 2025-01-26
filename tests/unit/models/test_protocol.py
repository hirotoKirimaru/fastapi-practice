# TODO: 処理途中
# from typing import Protocol, Any
# from sqlalchemy.ext.asyncio import AsyncSession
#
#
# class DownloadProtocol(Protocol):
#     async def __call__(
#         self,
#         session: AsyncSession,
#         date_start: str,
#         date_end: str,
#     ) -> Any: ...
#
# DownloadCallable = DownloadProtocol
#
# class DownloadUtil:
#     @staticmethod
#     async def download_file(callback_method: DownloadCallable, **kwargs) -> Any:
#         return callback_method(**kwargs)
#
#
#
# class TestDownload:
#     async def test_01(self, session: AsyncSession) -> None:
#         DownloadUtil.download_file(session, )
#

