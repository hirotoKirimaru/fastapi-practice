from dataclasses import dataclass
from enum import IntEnum

import pytest
from pydantic import BaseModel
from pydantic.v1 import PatternError


class PatternEnum(IntEnum):
    A = 0
    B = 1


class TestToJson:

    class CustomModel(BaseModel):
        id: str
        value: str
        pattern: PatternEnum

    def test_to_json(self):
        expected = {
            "id": "aaa",
            "value": "ccc",
            "pattern": 1
        }
        b = {
            "id": "aaa",
            "value": "ccc",
            "pattern": 1
        }

        assert expected == b

        c = self.CustomModel(
            id="aaa",
            value="ccc",
            pattern=1
        )

        # 単体テストとしては通るが…
        assert expected == c.model_dump()
        assert expected == c.model_dump(mode='json')

        # {'id': 'aaa', 'value': 'ccc', 'pattern': <PatternEnum.B: 1>}
        # {'id': 'aaa', 'value': 'ccc', 'pattern': 1}
