from functools import wraps
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

@pytest.mark.asyncio
async def test_01(db: AsyncSession) -> None:
    user1 = User(id=1, name="11", email="a@example.com", organization="開発部")
    await db.add(user1)
    await db.commit();

    query: select = select(User)

    actual = await db.query(query).first()

    assert user1.id == actual.id

