from typing import Annotated, Any, List

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.schemas.base import CustomModel

router = APIRouter()


class ExceptionInput(BaseModel):
    age: int = Field(ge=18)


class ErrorMessage(CustomModel):
    reason: str
    indexes: Annotated[
        List[int], Field(description="エラーが発生したインデックスのリスト")
    ]


class ExceptionResponse(CustomModel):
    detail: Annotated[
        str, Field(description="Exception detail", examples=["File Invalid"])
    ]
    error_lists: Annotated[
        List[ErrorMessage],
        Field(
            description="Exception details",
            examples=[{"reason": "Not Found", "indexes": [1, 2, 3]}],
        ),
    ]


@router.put("/exception")
async def exception(input_: ExceptionInput = Body(...)) -> Any:
    raise Exception()


# @router.get("/exception", responses={422: {"model": ExceptionResponse, "description": "Validation Error"}})
@router.get("/exception", responses={422: {"model": ExceptionResponse}})
async def file_invalid() -> Any:
    return JSONResponse(
        status_code=422,
        content=ExceptionResponse(detail="File Invalid", error_lists=[]).model_dump(
            by_alias=True
        ),
    )
