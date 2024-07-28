import pytest

from sqlalchemy import and_, select
from src.models.user import User


@pytest.mark.skipif(True, reason="再現できず。")
# Python3.12
# SQLAlchemy 2.0.27 なら再現できる？
# これを再現したかった。
# E sqlalchemy.exc.NoInspectionAvailable: No inspection system is available for object of type <class 'models.User>
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
        # assert user1 == actual
        # THEN
        db.add(actual)
        await db.commit()

    async def test_02(self, db):
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        db.add(user1)
        # await db.commit() # commitなら問題ない？
        await db.flush()
        copied_user = user1.__dict__
        copied_user.pop("_sa_instance_state")

        query: select = select(User)

        condition = and_(User.id == 1)

        query = query.where(condition)
        actual = (await db.execute(query)).scalars().first()

        # assert user1.id == actual.id
        # assert user1 == actual
        # THEN
        db.add(actual)
        await db.commit()
