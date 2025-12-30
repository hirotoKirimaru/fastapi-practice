import json
from datetime import datetime
from enum import IntEnum, Enum

import pytest
from pydantic import BaseModel

from src.helper.datetime_resolver import DatetimeResolver


class PatternEnum(IntEnum):
    A = 0
    B = 1


class Pattern2Enum(str, Enum):
    A = 0
    B = 1


class TestToJson:

    class CustomModel(BaseModel):
        id: str
        value: str
        pattern: PatternEnum
        # pattern2: Pattern2Enum | None = None
        now: datetime | None

    def test_to_json(self):
        now = DatetimeResolver.now()

        expected = {
            "id": "aaa",
            "value": "ccc",
            "pattern": 1,
            "now": now,
            # "pattern2": "0",
        }
        b = {
            "id": "aaa",
            "value": "ccc",
            "pattern": 1,
            "now": now,
            # "pattern2": "0",
        }

        assert expected == b

        c = self.CustomModel(
            id="aaa",
            value="ccc",
            pattern=1,
            now=now,
            # pattern2="0"
        )

        # 単体テストとしては通るが…
        assert expected == c.model_dump()
        # 文字列のシリアライズがうまくいかない
        assert expected != c.model_dump(mode="json")
        with pytest.raises(TypeError):
            assert expected == json.dumps(c.model_dump())
        assert expected != json.dumps(c.model_dump(mode="json"))

        # {'id': 'aaa', 'value': 'ccc', 'pattern': <PatternEnum.B: 1>}
        # {'id': 'aaa', 'value': 'ccc', 'pattern': 1}
