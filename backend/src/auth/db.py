from datetime import datetime
from typing import Any

from fastapi_users.db import BaseUserDatabase
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select
from sqlmodel.sql.expression import SelectOfScalar

from src.helper.datetime_resolver import DatetimeResolver
from src.models.access_token import AccessToken
from src.models.user import User


class SQLModelUserDatabase(BaseUserDatabase[User, int]):
    """fastapi-users のユーザ DB アダプタ。

    公式の fastapi-users-db-sqlalchemy は SQLAlchemy < 2.1 に固定されていて、独自の
    DeclarativeBase を要求するので使わず、既存の SQLModel の User に合わせて書く。
    - 論理削除（soft_destroyed_at）されたユーザは居ないものとして扱う
    - 削除（DELETE /users/{id}, /users/me）は論理削除にする。posts などが参照しているため
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _alive(self) -> SelectOfScalar[User]:
        return select(User).where(col(User.soft_destroyed_at).is_(None))

    async def get(self, id: int) -> User | None:
        return (
            await self.session.execute(self._alive().where(User.id == id))
        ).scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        # 大文字小文字を区別しない（Foo@Example.com と foo@example.com を別人にしない）
        query = self._alive().where(func.lower(col(User.email)) == email.lower())
        return (await self.session.execute(query)).scalars().first()

    async def create(self, create_dict: dict[str, Any]) -> User:
        user = User(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        user.soft_destroyed_at = DatetimeResolver.now()
        user.is_active = False
        self.session.add(user)
        await revoke_all_tokens(self.session, user, commit=False)
        await self.session.commit()


class SQLModelAccessTokenDatabase:
    """fastapi-users の DatabaseStrategy が使うトークンのアダプタ（AccessTokenDatabase）"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_token(
        self, token: str, max_age: datetime | None = None
    ) -> AccessToken | None:
        query = select(AccessToken).where(AccessToken.token == token)
        if max_age is not None:
            query = query.where(col(AccessToken.created_at) >= max_age)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def create(self, create_dict: dict[str, Any]) -> AccessToken:
        access_token = AccessToken(**create_dict)
        self.session.add(access_token)
        await self.session.commit()
        await self.session.refresh(access_token)
        return access_token

    async def update(
        self, access_token: AccessToken, update_dict: dict[str, Any]
    ) -> AccessToken:
        for key, value in update_dict.items():
            setattr(access_token, key, value)
        self.session.add(access_token)
        await self.session.commit()
        await self.session.refresh(access_token)
        return access_token

    async def delete(self, access_token: AccessToken) -> None:
        await self.session.delete(access_token)
        await self.session.commit()


async def revoke_all_tokens(
    session: AsyncSession, user: User, *, commit: bool = True
) -> None:
    """そのユーザのトークンを全部消す（全端末からログアウト）"""
    await session.execute(
        delete(AccessToken).where(col(AccessToken.user_id) == user.id)
    )
    if commit:
        await session.commit()
