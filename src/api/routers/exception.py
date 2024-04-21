from typing import Any

from pydantic import BaseModel, Field

from fastapi import APIRouter, Body

router = APIRouter()


class ExceptionInput(BaseModel):
    age: int = Field(ge=18)


@router.put("/exception")
async def exception(input_: ExceptionInput = Body(...)) -> Any:
    raise Exception()
