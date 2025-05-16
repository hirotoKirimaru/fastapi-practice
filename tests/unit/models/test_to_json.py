import json
from dataclasses import dataclass
from enum import IntEnum, Enum

import pytest
from pydantic import BaseModel
from pydantic.v1 import PatternError


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

    def test_to_json(self):
        expected = {
            "id": "aaa",
            "value": "ccc",
            "pattern": 1,
            # "pattern2": "0",
        }
        b = {
            "id": "aaa",
            "value": "ccc",
            "pattern": 1,
            # "pattern2": "0",
        }

        assert expected == b

        c = self.CustomModel(
            id="aaa",
            value="ccc",
            pattern=1,
            # pattern2="0"
        )

        # 単体テストとしては通るが…
        assert expected == c.model_dump()
        assert expected == c.model_dump(mode='json')

        # {'id': 'aaa', 'value': 'ccc', 'pattern': <PatternEnum.B: 1>}
        # {'id': 'aaa', 'value': 'ccc', 'pattern': 1}
