from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.notification
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from src.db import get_reader_db
from src.schemas.notification import Notification as schema_notification

router = APIRouter()

async def read():
    print("XXXXXXXXXXXXXXXXX")

@router.post("/unread", response_model=schema_notification)
async def read_unread_notifications(
    tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_reader_db),
) -> Any:
    tasks.add_task(read)
    return schema_notification(description= "123")
