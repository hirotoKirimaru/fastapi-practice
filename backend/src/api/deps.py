from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.helper.config import settings
from src.helper.security import decode_access_token
from src.models.user import User

async_engine = create_async_engine(settings.DATABASE_URL, echo=settings.SQL_ECHO)
# async_session = sessionmaker(
#     autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
# )
# async_session = sessionmaker(bind=async_engine, class_=AsyncSession)
# async_session = sessionmaker(class_=AsyncSession)
# async_session = async_sessionmaker(
#     autoflush=False, expire_on_commit=False, bind=async_engine, class_=AsyncSession
# )
async_session = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False
)

# Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession]:
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


async def get_writer_db() -> AsyncGenerator[AsyncSession]:
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


async def get_reader_db() -> AsyncGenerator[AsyncSession]:
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


SessionWriterDep = Annotated[AsyncSession, Depends(get_writer_db)]
SessionReaderDep = Annotated[AsyncSession, Depends(get_reader_db)]


# 認証。Authorization: Bearer <JWT> を読み、トークンの sub のユーザを返す。
# tokenUrl は Swagger UI の Authorize ボタンがトークンを取りに行く先
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token", auto_error=False
)


async def get_user_from_token(db: AsyncSession, token: str | None) -> User | None:
    """トークンが無い・不正・期限切れ・ユーザが消えている（論理削除を含む）ときは None"""
    if not token:
        return None
    sub = decode_access_token(token)
    if sub is None or not sub.isdecimal():
        return None
    user = await db.get(User, int(sub))
    if user is None or user.soft_destroyed_at is not None:
        return None
    return user


async def get_current_user(
    db: SessionReaderDep, token: Annotated[str | None, Depends(oauth2_scheme)]
) -> User:
    user = await get_user_from_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
