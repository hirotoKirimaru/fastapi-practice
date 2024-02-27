from typing import Any

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field


router = APIRouter()


class ExceptionInput(BaseModel):
    age: int = Field(ge=18)


@router.put("/exception")
async def exception(input_: ExceptionInput = Body(...)) -> Any:
    raise Exception()
