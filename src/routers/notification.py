from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
import src.schemas.notification
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from src.db import get_reader_db
from src.schemas.notification import Notification as schema_notification
from src.helper.datetime_resolver import DatetimeResolver

router = APIRouter()

async def read(db, read_time: datetime):
    # TODO: あれ、Serializeしなくても渡せる…？
    print(db)
    print(read_time)
    print("XXXXXXXXXXXXXXXXX")

@router.post("/unread", response_model=schema_notification)
async def read_unread_notifications(
    tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_reader_db),
) -> Any:
    tasks.add_task(read, db=db, read_time=DatetimeResolver.now())
    return schema_notification(description= "123")
