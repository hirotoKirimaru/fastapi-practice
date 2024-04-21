from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, BackgroundTasks, Depends
from src.helper.datetime_resolver import DatetimeResolver
from src.schemas.notification import Notification as schema_notification
from src.api.deps import SessionWriterDep, SessionReaderDep

router = APIRouter()


async def read(db: SessionWriterDep, read_time: datetime):
    # TODO: あれ、Serializeしなくても渡せる…？
    print(db)
    print(read_time)
    print("XXXXXXXXXXXXXXXXX")


@router.post("/unread", response_model=schema_notification)
async def read_unread_notifications(
    tasks: BackgroundTasks,
    db: SessionReaderDep,
) -> Any:
    tasks.add_task(read, db=db, read_time=DatetimeResolver.now())
    return schema_notification(description="123")
