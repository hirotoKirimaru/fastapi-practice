from typing import AsyncGenerator, List, Optional, Tuple

import src.models.task as task_model
import src.schemas.task as task_schema
from sqlalchemy import select, and_
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.csvs import Csvs


async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    task = task_model.Task(**task_create.dict())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_with_done(db: AsyncSession) -> List[Tuple[int, str, bool]]:
    result: Result = await (
        db.execute(
            select(
                task_model.Task.id,
                task_model.Task.title,
                task_model.Done.id.isnot(None).label("done"),
            ).outerjoin(task_model.Done)
        )
    )
    return result.all()


async def get_tasks_with_done_inner_join(
    db: AsyncSession,
) -> List[Tuple[int, str, bool]]:
    result: Result = await (
        db.execute(
            select(
                task_model.Task.id,
                task_model.Task.title,
                task_model.Done.id.isnot(None).label("done"),
            ).join(task_model.Task, task_model.Done.task)
        )
    )
    return result.all()


# async def get_task(db: AsyncSession, task_id: int, criteria: and_ | None = None) -> Optional[task_model.Task]:
# async def get_task(db: AsyncSession, task_id: int, criteria: Optional[and_ ] = None) -> Optional[task_model.Task]:
async def get_task(db: AsyncSession, task_id: int, criteria: Optional[and_ ] = None) -> Optional[task_model.Task]:
    result: Result = await db.execute(
        select(task_model.Task).filter(task_model.Task.id == task_id)
    )
    task: Optional[Tuple[task_model.Task]] = result.first()
    return task[0] if task is not None else None  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す


async def update_task(
    db: AsyncSession, task_create: task_schema.TaskCreate, original: task_model.Task
) -> task_model.Task:
    original.title = task_create.title
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
