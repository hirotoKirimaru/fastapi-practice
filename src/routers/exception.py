from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.done as done_schema
import src.cruds.done as done_crud
from src.db import get_db

router = APIRouter()

class ExceptionInput(BaseModel):
    age: int = Field(ge=18)
@router.put("/exception")
async def exception(input_: ExceptionInput) -> Any:
    raise Exception()
