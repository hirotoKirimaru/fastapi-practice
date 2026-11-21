"""最初の管理者（settings.FIRST_SUPERUSER）が居なければ作る。何度実行してもよい。

full-stack-fastapi-template の initial_data.py に相当。マイグレーションの後に流す:
    uv run alembic upgrade head && uv run python -m src.initial_data
"""

import asyncio
import contextlib
import logging

from fastapi_users.exceptions import UserAlreadyExists

from src.api.deps import async_session
from src.auth.db import SQLModelUserDatabase
from src.auth.manager import UserManager
from src.helper.config import settings
from src.schemas.auth import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_superuser() -> None:
    async with async_session() as session:
        manager = UserManager(SQLModelUserDatabase(session))
        with contextlib.suppress(UserAlreadyExists):
            await manager.create(
                UserCreate(
                    name="admin",
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                    is_verified=True,
                )
            )
            logger.info("created first superuser: %s", settings.FIRST_SUPERUSER)


if __name__ == "__main__":
    asyncio.run(create_first_superuser())
