from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import joinedload

import pytest

# import logging
from src.models.user import User
from src.models.organization import Organization


async def test_01(db: AsyncSession) -> None:
    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
    user2 = User(id=2, name="11", email="a@example.com", organization_id=1)
    user3 = User(id=3, name="11", email="a@example.com", organization_id=1)
    db.add(user1)
    db.add(user2)
    db.add(user3)
    await db.commit()

    query: select = select(User)

    condition = and_(User.id == 1)

    query = query.where(condition)
    actual = (await db.execute(query)).scalars().all()

    # assert user1.id == actual[0].id
    assert len(actual) == 1


async def test_02(db: AsyncSession) -> None:
    user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
    user2 = User(id=2, name="11", email="a@example.com", organization_id=1)
    user3 = User(id=3, name="11", email="a@example.com", organization_id=1)
    db.add(user1)
    db.add(user2)
    db.add(user3)
    await db.commit()

    query: select = select(User)

    # 最後の条件で上書き
    condition = and_(User.id == 1)
    condition = and_(User.organization_id == 1)

    query = query.where(condition)
    actual = (await db.execute(query)).scalars().all()

    # assert user1.id == actual[0].id
    assert len(actual) == 3


async def test_03(db: AsyncSession) -> None:
    user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
    user2 = User(id=2, name="11", email="a@example.com", organization_id=1)
    user3 = User(id=3, name="11", email="a@example.com", organization_id=1)
    db.add(user1)
    db.add(user2)
    db.add(user3)
    await db.commit()

    query: Select = select(User)

    # 条件をまとめる
    criteria = []
    criteria.append(and_(User.id == 1))
    criteria.append(and_(User.organization_id == 1))

    query = query.where(*criteria)
    actual = (await db.execute(query)).scalars().all()

    # assert user1.id == actual[0].id
    assert len(actual) == 1

class TestUserRelationShip:
    async def test_01(self, db: AsyncSession):
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        db.add(user1)
        await db.commit()

        query: Select = select(User).where(User.id == 1)
        result = (await db.execute(query)).scalars().first()
        with pytest.raises(MissingGreenlet) as e:
            _ = result.organization

    async def test_02(self, db: AsyncSession):
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        organization_1 = Organization(id=1)
        db.add(user1)
        db.add(organization_1)
        await db.commit()

        query: Select = (select(User)
                         .options(joinedload(User.organization))
                         .where(User.id == 1))
        result = (await db.execute(query)).scalars().first()
        assert result.organization is not None

    async def test_not_lazy_default(self, db: AsyncSession):
        """
        lazyがselectだけダメな模様？


        :param db:
        :return:
        """
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        organization_1 = Organization(id=1)
        db.add(user1)
        db.add(organization_1)
        await db.commit()

        query: Select = (select(User)
                         .where(User.id == 1))
        result = (await db.execute(query)).scalars().first()
        assert result.organization2 is not None
        assert result.organization3 is None