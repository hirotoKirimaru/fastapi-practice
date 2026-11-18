from typing import Any

from fastapi import APIRouter, HTTPException

import src.crud.done as done_crud
import src.crud.task as task_crud
import src.schemas.done as done_schema
from src.api.deps import SessionWriterDep

router = APIRouter()


@router.put("/{task_id}/done", response_model=done_schema.DoneResponse)
async def mark_task_as_done(task_id: int, db: SessionWriterDep) -> Any:
    # 存在しないタスクに完了を付けると dones の外部キーに違反して 500 になっていた
    # （SQLite の頃は外部キーが検査されず、親の無い Done ができていた）
    if await task_crud.get_task(db, task_id=task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")

    done = await done_crud.get_done(db, task_id=task_id)
    if done is not None:
        raise HTTPException(status_code=400, detail="Done already exists")

    return await done_crud.create_done(db, task_id)


@router.delete("/{task_id}/done", response_model=None)
async def unmark_task_as_done(task_id: int, db: SessionWriterDep) -> Any:
    done = await done_crud.get_done(db, task_id=task_id)
    if done is None:
        raise HTTPException(status_code=404, detail="Done not found")

    return await done_crud.delete_done(db, original=done)
