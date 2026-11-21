from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_writer_db
from src.auth.db import SQLModelAccessTokenDatabase, SQLModelUserDatabase
from src.auth.manager import UserManager
from src.helper.config import settings
from src.models.access_token import AccessToken
from src.models.user import User


# セッションはルーター側（SessionWriterDep）と同じ get_writer_db から取る。FastAPI は 1 リクエスト内で
# 同じ依存を使い回すので、認証とルーターの処理が 1 つのセッション（＝1 接続）を共有する
async def get_user_db(
    session: AsyncSession = Depends(get_writer_db),
) -> AsyncGenerator[SQLModelUserDatabase]:
    yield SQLModelUserDatabase(session)


async def get_access_token_db(
    session: AsyncSession = Depends(get_writer_db),
) -> AsyncGenerator[SQLModelAccessTokenDatabase]:
    yield SQLModelAccessTokenDatabase(session)


async def get_user_manager(
    user_db: SQLModelUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager]:
    yield UserManager(user_db)


def get_database_strategy(
    access_token_db: SQLModelAccessTokenDatabase = Depends(get_access_token_db),
) -> DatabaseStrategy[User, int, AccessToken]:
    return DatabaseStrategy(
        access_token_db, lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# Authorization: Bearer <token>。tokenUrl は Swagger UI の Authorize ボタンがログインしに行く先
bearer_transport = BearerTransport(
    tokenUrl=f"{settings.API_V1_STR}/auth/login".lstrip("/")
)

auth_backend = AuthenticationBackend(
    name="db", transport=bearer_transport, get_strategy=get_database_strategy
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

CurrentUser = Annotated[User, Depends(current_active_user)]
CurrentSuperuser = Annotated[User, Depends(current_superuser)]
