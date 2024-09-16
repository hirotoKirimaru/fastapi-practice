from typing import Annotated, Any, List, Dict

from pydantic import BaseModel, ConfigDict, Field, Json

from src.schemas.base import CustomModel

JsonField = Annotated[
    Json[Any] | Dict[str, Any] | List[Any] | None,
    Field(description="JSON文字列、辞書、リスト、またはNoneを受け取るために使用するフィールドです。", default=None, examples=['{"value": {"a": "b"}}', ["A", "B"], {'value': [{'a': 'b'}]}]),
]

class Question(CustomModel):
    title: str
    selectable: JsonField


