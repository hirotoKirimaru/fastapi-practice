from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.task import Task, Done


class TestTaskCascade:
    async def test_01(self, db: AsyncSession) -> None:
        """
        Taskを削除したときに子テーブルのDoneも削除すること。
        """
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

        # WHEN
        print("XXXXXX")
        await db.delete(task1)
        await db.commit()
        print("XXXXXX")

        # THEN
        query: select = select(Task).options(joinedload(Task.done))
        actual = (await db.execute(query)).scalars().all()
        assert {2, 3} == {x.id for x in actual}

        # THEN
        query: select = select(Done)
        actual = (await db.execute(query)).scalars().all()
        assert {2, 3} == {x.id for x in actual}

