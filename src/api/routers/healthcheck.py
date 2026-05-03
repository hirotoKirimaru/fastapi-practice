# -*- coding: utf-8 -*-


from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@router.get("-check/")
async def health_check() -> bool:
    return True
