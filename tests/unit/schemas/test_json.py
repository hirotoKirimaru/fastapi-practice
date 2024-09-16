import json
import pytest
from typing import Annotated, Dict, Any, List

from pydantic import BaseModel, Json, Field, ValidationError


JsonField = Annotated[
    Json[Any] | Dict[str, Any] | List[Any] | None,
    Field(description="JSON文字列、辞書、リスト、またはNoneを受け取るために使用するフィールドです。", default=None, examples=['{"value": {"a": "b"}}', ["A", "B"], {'value': [{'a': 'b'}]}]),
]

class TestJson:
    class _Test(BaseModel):
        value: Json

    class _Test2(BaseModel):
        value: JsonField

    @pytest.mark.parametrize(
        "value, expected_raise",
        [
            ('{"value": {"a": "b"}}', False),
            (["A, B"], True),
            ({'value': [{'a': 'b'}]}, True)
        ],
    )
    async def test_01(self, value: Any, expected_raise: bool):
        # instance = self._Test(value=["foo", "bar", "baz"])
        # instance = self._Test(value=json.dumps(["foo", "bar", "baz"]))
        instance = self._Test(value=json.dumps(value))
        if expected_raise:
            with pytest.raises(ValidationError):
                self._Test.model_validate(instance.model_dump())
        else:
            self._Test.model_validate(instance.model_dump())

    @pytest.mark.parametrize(
        "value",
        [
            '{"value": {"a": "b"}}',
            ["A, B"],
            {'value': [{'a': 'b'}]}
        ],
    )
    async def test_02(self, value: Any):
        # instance = self._Test(value=["foo", "bar", "baz"])
        # instance = self._Test(value=json.dumps(["foo", "bar", "baz"]))
        instance = self._Test2(value=value)
        self._Test2.model_validate(instance.model_dump())