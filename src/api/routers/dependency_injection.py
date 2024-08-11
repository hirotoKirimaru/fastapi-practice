from datetime import datetime
from typing import Any, Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from src.helper.datetime_resolver import DatetimeResolver
from src.schemas.notification import Notification as schema_notification
from src.api.deps import SessionWriterDep, SessionReaderDep

router = APIRouter()

class DIClass:
    def __init__(self, msg: str):
        self.msg = msg

    async def __call__(
        self,
    ):
        print(self.msg)

# TODO: なぜか使えなかった
AsyncDi = Annotated[None, Depends(DIClass(msg="ASYNC TWO"))]


async def async_printer(msg: str) -> None:
    print(msg)

def printer(msg: str) -> None:
    print(msg)


@router.post("/run", response_model=bool)
async def read_unread_notifications(
    _: None = Depends(lambda: printer(msg="SYNC")),
    __: None = Depends(lambda: async_printer(msg="ASYNC")),
    ___: None = Depends(DIClass(msg="ASYNC TWO")),
    # ____: AsyncDi,
) -> Any:
    return True