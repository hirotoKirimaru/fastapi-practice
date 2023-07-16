from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from src.models.user import User

@pytest.mark.asyncio
async def test_01(db: AsyncSession) -> None:
    user1 = User(id=1, name="11", email="a@example.com", organization="開発部")
    
    db.add(user1)
    await db.commit();

    query: select = select(User)

    actual = (await db.execute(query)).scalars().all()

    assert user1.id == actual[0].id

