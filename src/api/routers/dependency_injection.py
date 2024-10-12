from typing import Any, Annotated, Callable

from fastapi import APIRouter, Depends, Security, UploadFile, File

from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import SessionWriterDep, SessionReaderDep

router = APIRouter()


class DIClass:
    def __init__(self, msg: str):
        self.msg = msg

    async def __call__(
        self,
    ):
        print(self.msg)


AsyncDi = Annotated[None, Depends(DIClass(msg="ASYNC THREE"))]


async def async_printer(msg: str) -> None:
    print(msg)


def printer(msg: str) -> None:
    print(msg)


@router.post("/run", response_model=bool)
async def di_test(
    *,
    _: None = Depends(lambda: printer(msg="SYNC")),
    __: None = Depends(lambda: async_printer(msg="ASYNC")),
    ___: None = Depends(DIClass(msg="ASYNC TWO")),
    ____: AsyncDi,
) -> Any:
    return True


async def get_current_user() -> None:
    pass


class CsvFileValidator:
    """
    処理に必要なものをDIで取得する共通部品
    """

    def __init__(
        self, validator: Callable[[AsyncSession, UploadFile, None], bool]
    ) -> Any:
        self.validator = validator

    async def __call__(
        self,
        session: SessionReaderDep,  # Validate処理でReaderインスタンスを取得する
        file: UploadFile = File(...),
        current_user=Security(get_current_user),
    ) -> Any:
        return await self.validator(session, file, current_user)


async def csv_validation(
    session: AsyncSession, file: UploadFile, current_user: User
) -> None:
    """
    具体的なチェック処理
    """
    pass


FileValidated = Annotated[None, Depends(CsvFileValidator(csv_validation))]


@router.post("/run2", response_model=bool)
async def csv_register(
    *,
    sesison: SessionWriterDep,  # 本処理ではWriterインスタンスを使用する
    _: FileValidated,  # DI時にバリデーションをしてくれる
) -> Any:
    return True
