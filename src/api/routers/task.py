from typing import List

from fastapi.responses import StreamingResponse

import src.cruds.task as task_crud
import src.schemas.task as task_schema
from fastapi import APIRouter, Depends, HTTPException
from src.api.deps import SessionWriterDep

router = APIRouter()


@router.get("", response_model=List[task_schema.Task])
async def list_tasks(db: SessionWriterDep):
    return await task_crud.get_tasks_with_done(db)


@router.post("", response_model=task_schema.TaskCreateResponse)
async def create_task(
    task_body: task_schema.TaskCreate, db: SessionWriterDep
):
    return await task_crud.create_task(db, task_body)


@router.put("/{task_id}", response_model=task_schema.TaskCreateResponse)
async def update_task(
    task_id: int, task_body: task_schema.TaskCreate, db: SessionWriterDep
):
    task = await task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return await task_crud.update_task(db, task_body, original=task)


@router.delete("/{task_id}", response_model=None)
async def delete_task(task_id: int, db: SessionWriterDep):
    task = await task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return await task_crud.delete_task(db, original=task)


@router.get("/download")
async def download_task(db: SessionWriterDep):
    return StreamingResponse(
        task_crud.create_csv(),
        headers={"Content-Disposition": 'attachment; filename="file.txt"'},
    )
