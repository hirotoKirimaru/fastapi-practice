
import pytest

import src.cruds
from src.models.task import Task, Done


class TestTask:
    class TestGetTasksWithDone:

        @pytest.mark.asyncio
        async def test_get_single(self, db):
            # Given
            task1 = Task(title="ダミー1")
            db.add(task1)

            await db.commit()
            await db.refresh(task1)

            # WHEN
            actual = await src.cruds.task.get_tasks_with_done(db)

            # THEN
            assert len(actual) == 1
            assert actual == [(1, "ダミー1", False)]

        @pytest.mark.asyncio
        async def test_get_multiple(self, db):
            # Given
            task1 = Task(title="ダミー1")
            task2 = Task(title="ダミー2")
            db.add(task1)
            db.add(task2)

            await db.commit()
            await db.refresh(task1)
            await db.refresh(task2)

            # WHEN
            actual = await src.cruds.task.get_tasks_with_done(db)

            # THEN
            assert len(actual) == 2
            assert actual == [(1, "ダミー1", False), (2, "ダミー2", False)]

    class TestGetTasksWithDoneInnerJoin:

        @pytest.mark.asyncio
        async def test_get_single(self, db):
            # Given
            task1 = Task(title="ダミー1")
            db.add(task1)

            await db.commit()
            await db.refresh(task1)

            done1 = Done(id=task1.id)
            db.add(done1)

            await db.commit()
            await db.refresh(done1)

            # WHEN
            actual = await src.cruds.task.get_tasks_with_done_inner_join(db)

            # THEN
            assert len(actual) == 1
            assert actual == [(1, "ダミー1", True)]

        @pytest.mark.asyncio
        async def test_get_multiple(self, db):
            # Given
            task1 = Task(title="ダミー1")
            task2 = Task(title="ダミー2")
            db.add(task1)
            db.add(task2)

            await db.commit()
            await db.refresh(task1)
            await db.refresh(task2)

            done1 = Done(id=task1.id)
            done2 = Done(id=task2.id)
            db.add(done1)
            db.add(done2)

            await db.commit()
            await db.refresh(done1)
            await db.refresh(done2)

            # WHEN
            actual = await src.cruds.task.get_tasks_with_done_inner_join(db)

            # THEN
            assert len(actual) == 2
            assert actual == [(1, "ダミー1", True), (2, "ダミー2", True)]