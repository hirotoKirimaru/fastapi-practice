import pprint

import pytest
from sqlalchemy.ext.asyncio import async_session, create_async_engine

import src.cruds.task
from src.models.task import Task


@pytest.mark.asyncio
async def test_get_tasks_with_done_2(db):
    # Given
    task1 = Task(title="ダミー1")
    task2 = Task(title="ダミー2")
    db.add(task1)
    db.add(task2)

    await db.commit()
    await db.refresh(task1)
    await db.refresh(task2)

    actual = await src.cruds.task.get_tasks_with_done_2(db)
    print("**********")
    pprint.pprint(actual)

    assert len(actual) == 2
    assert actual == [(1, "ダミー1", False), (2, "ダミー2", False)]