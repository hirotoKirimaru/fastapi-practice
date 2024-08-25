from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.task import Task, Done


class TestTaskCascade:
    async def test_01(self, db: AsyncSession) -> None:
        task1 = Task(id=1, title="Test1")
        task2 = Task(id=2, title="Test1")
        task3 = Task(id=3, title="Test1")
        db.add(task1)
        db.add(task2)
        db.add(task3)

        done1 = Done(id=1)
        done2 = Done(id=2)
        done3 = Done(id=3)
        db.add(done1)
        db.add(done2)
        db.add(done3)
        await db.commit()

        query: select = select(Task).options(joinedload(Task.done))

        # condition = and_(User.id == 1)

        # query = query.where(condition)
        actual = (await db.execute(query)).scalars().all()

        # assert user1.id == actual[0].id
        breakpoint()
        assert len(actual) == 1

