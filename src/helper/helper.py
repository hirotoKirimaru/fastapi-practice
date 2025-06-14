import logging
import time
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@asynccontextmanager
async def session_context(session: AsyncSession) -> None:
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


@asynccontextmanager
async def timeit(operation_name: str = "Operation"):
    """
    処理時間を計測し、開始と終了時にログを出力するコンテキストマネージャー

    Args:
        operation_name: 操作名（ログに表示される）
    """
    start_time = time.time()
    logger.info(f"[{operation_name}] 処理開始")

    try:
        yield
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"[{operation_name}] 処理完了 - 実行時間: {elapsed_time:.4f}秒")

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """
        呼出元にエラーが発生したときに伝播させたいので、Falseを常に返却する。
        発生しないと、全てのエラーがcontext_managerの行で発生したことになる。
        """
        return False