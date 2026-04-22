from datetime import datetime
from typing import Optional

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.post import Post as PostModel
from src.models.user import User as UserModel


@strawberry.type
class Post:
    id: int
    title: str
    user_id: int


@strawberry.type
class User:
    id: int
    name: str
    email: str
    organization_id: Optional[int] = None
    birth_day: Optional[datetime] = None


@strawberry.type
class Query:
    @strawberry.field
    async def hello(self, name: str = "world") -> str:
        return f"Hello, {name}!"

    @strawberry.field
    async def users(self, info: strawberry.Info) -> list[User]:
        session: AsyncSession = info.context["session"]
        result = await session.execute(select(UserModel))
        rows = result.scalars().all()
        return [
            User(
                id=u.id,
                name=u.name,
                email=u.email,
                organization_id=u.organization_id,
                birth_day=u.birth_day,
            )
            for u in rows
            if u.id is not None
        ]

    @strawberry.field
    async def user(self, info: strawberry.Info, id: int) -> Optional[User]:
        session: AsyncSession = info.context["session"]
        result = await session.execute(select(UserModel).where(UserModel.id == id))
        u = result.scalar_one_or_none()
        if u is None or u.id is None:
            return None
        return User(
            id=u.id,
            name=u.name,
            email=u.email,
            organization_id=u.organization_id,
            birth_day=u.birth_day,
        )

    @strawberry.field
    async def posts(self, info: strawberry.Info) -> list[Post]:
        session: AsyncSession = info.context["session"]
        result = await session.execute(select(PostModel))
        rows = result.scalars().all()
        return [
            Post(id=p.id, title=p.title, user_id=p.user_id)
            for p in rows
            if p.id is not None
        ]


@strawberry.input
class UserCreateInput:
    name: str
    email: str
    organization_id: Optional[int] = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self, info: strawberry.Info, input: UserCreateInput
    ) -> User:
        session: AsyncSession = info.context["session"]
        user = UserModel(
            name=input.name,
            email=input.email,
            organization_id=input.organization_id,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        assert user.id is not None
        return User(
            id=user.id,
            name=user.name,
            email=user.email,
            organization_id=user.organization_id,
            birth_day=user.birth_day,
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
