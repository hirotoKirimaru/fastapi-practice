from sqlalchemy.ext.asyncio import AsyncSession

import src.cruds.done as done_crud
import src.schemas.done as done_schema
from fastapi import APIRouter, Depends, HTTPException
from src.db import get_db

router = APIRouter()


@router.put("/{task_id}/done", response_model=done_schema.DoneResponse)
async def mark_task_as_done(task_id: int, db: AsyncSession = Depends(get_db)):
    done = await done_crud.get_done(db, task_id=task_id)
    if done is not None:
        raise HTTPException(status_code=400, detail="Done already exists")

    return await done_crud.create_done(db, task_id)


@router.delete("/{task_id}/done", response_model=None)
async def unmark_task_as_done(task_id: int, db: AsyncSession = Depends(get_db)):
    done = await done_crud.get_done(db, task_id=task_id)
    if done is None:
        raise HTTPException(status_code=404, detail="Done not found")

    return await done_crud.delete_done(db, original=done)
