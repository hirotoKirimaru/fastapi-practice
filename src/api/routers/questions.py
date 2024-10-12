from typing import Any, List

from fastapi import APIRouter

from src.schemas.json import Question

router = APIRouter()


@router.get("/", response_model=List[Question])
async def find_questions() -> Any:
    return [Question(title="AAA", selectable=[1, 2, 3])]
