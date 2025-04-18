from typing import Any

from fastapi import APIRouter

from src.api.deps import SessionReaderDep
from src.schemas.gemini import GeminiInput
from src.usecase.usecase_gen import Gemini

router = APIRouter()


@router.post("/gemini", response_model=str)
async def generate_by_gemini(db: SessionReaderDep, _input: GeminiInput) -> Any:
    async with Gemini() as client:
        return await client.generate_content(_input.content)
