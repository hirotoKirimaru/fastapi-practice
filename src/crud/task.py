from typing import Any, AsyncGenerator, Optional, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

import src.models.task as task_model
import src.schemas.task as task_schema
from src.models.csvs import Csvs


async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    task = task_model.Task(**task_create.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_with_done(db: AsyncSession) -> Sequence[Row[Any]]:
    result: Result[Any] = await db.execute(
        select(  # type: ignore[call-overload]
            task_model.Task.id,
            task_model.Task.title,
            task_model.Done.id.is_not(None).label("done"),  # type: ignore[attr-defined]
        ).outerjoin(task_model.Done)
    )
    return result.all()


async def get_tasks_with_done_inner_join(
    db: AsyncSession,
) -> Sequence[Row[Any]]:
    query: Select[Any] = select(  # type: ignore[call-overload]
        task_model.Task.id,
        task_model.Task.title,
        task_model.Done.id.is_not(None).label("done"),  # type: ignore[attr-defined]
    ).join(task_model.Task, task_model.Done.task)

    return (await db.execute(query)).all()


# async def get_task(db: AsyncSession, task_id: int, criteria: and_ | None = None) -> Optional[task_model.Task]:
# async def get_task(db: AsyncSession, task_id: int, criteria: Optional[and_ ] = None) -> Optional[task_model.Task]:
async def get_task(
    db: AsyncSession, task_id: int, criteria: Optional[ColumnElement[Any]] = None
) -> Optional[task_model.Task]:
    result: Result[Any] = await db.execute(
        select(task_model.Task).filter(task_model.Task.id == task_id)  # type: ignore[arg-type]
    )
    task: Optional[Row[Tuple[task_model.Task]]] = result.first()
    return (
        task[0] if task is not None else None
    )  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す


async def update_task(
    db: AsyncSession, task_create: task_schema.TaskCreate, original: task_model.Task
) -> task_model.Task:
    original.title = task_create.title  # type: ignore
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original


async def delete_task(db: AsyncSession, original: task_model.Task) -> None:
    await db.delete(original)
    await db.commit()


async def create_csv() -> AsyncGenerator[bytes, None]:
    for i in range(100):
        yield Csvs.create_row_data(data=[i], first=i == 0)
