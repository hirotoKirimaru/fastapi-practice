from typing import Optional

import src.models.task as task_model
from sqlalchemy import select, and_
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from sqlalchemy.sql.elements import ColumnElement


async def base_query(task_id: int) -> ColumnElement:
    return and_(task_model.Done.id == task_id)


async def get_done(db: AsyncSession, task_id: int) -> Optional[task_model.Done]:
    criteria = await base_query(task_id)
    result: Result = await db.execute(select(task_model.Done).where(criteria))
    done: Row[task_model.Done] | None = result.first()
    return (
        done[0] if done is not None else None
    )  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す
