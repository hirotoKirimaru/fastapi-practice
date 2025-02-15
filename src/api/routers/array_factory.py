from typing import Annotated, List

from fastapi import APIRouter
from pydantic import Field

from src.schemas.base import CustomModel

router = APIRouter()


class CustomArray(CustomModel):
    # TODO: 実はどっちでもちゃんと安全に処理できる
    array: Annotated[List[str], Field(default=[])]
    array_factory: Annotated[List[str], Field(default_factory=list)]


def default_param(param: str, result: List[str] = []) -> List[str]:
    result.append(param)
    return result


@router.put("/test/array_factory", response_model=CustomArray)
async def test_array_factory():
    result = CustomArray()
    result2 = CustomArray()
    # print(result.model_dump())
    # 別にこれでもおんなじものっぽい
    print(result.model_dump(exclude_defaults=True))
    print(result2.model_dump(exclude_defaults=True))

    result.array.append("A")
    result.array_factory.append("A")
    result2.array.append("B")
    result2.array_factory.append("B")
    print(result)
    print(result2)
    _ = default_param("1")
    resultx = default_param("2")
    print(resultx)

    return result2
