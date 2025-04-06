import orjson
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter()

class Item(BaseModel):
    id: int
    name: str

class Item2(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        json_serializer=orjson.dumps,
    )


@router.get("/pydantic_only")
async def pydantic_only():
    return Item(id=1, name="Pydantic Model")


@router.get("/pydantic_with_orjson")
async def with_orjson():
    return Item2(id=1, name="Pydantic Model2")


