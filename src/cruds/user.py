from typing import Tuple, Optional

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import src.models.task as task_model


async def get_done(db: AsyncSession, task_id: int) -> Optional[task_model.Done]:
    criteria = self.base_query(task_id)
    result: Result = await db.execute(
        select(task_model.Done).where(criteria)
    )
    done: Optional[Tuple[task_model.Done]] = result.first()
    return done[0] if done is not None else None  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す


async def base_query(task_id: int) -> sqlalchemy.and_ | None:
    return and_(task_model.Done.id == task_id)