from typing import Any

from fastapi import APIRouter

from src.schemas.json import Question

router = APIRouter()


@router.get("/", response_model=list[Question])
async def find_questions() -> Any:
    return [Question(title="AAA", selectable=[1, 2, 3])]
