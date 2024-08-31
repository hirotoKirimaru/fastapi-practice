from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def session_context(session: AsyncSession) -> None:
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e