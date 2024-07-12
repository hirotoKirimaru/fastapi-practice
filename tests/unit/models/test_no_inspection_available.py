import pytest
from dataclasses import dataclass

from sqlalchemy import and_, select, func
from pydantic import BaseModel
from src.models.user import User


class TestNoInspectionAvailable:
    async def test_01(self, db):
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        db.add(user1)
        await db.commit()

        query: select = select(User)

        condition = and_(User.id == 1)

        query = query.where(condition)
        actual = (await db.execute(query)).scalars().first()

        # assert user1.id == actual.id
        assert user1 == actual