from dataclasses import dataclass

import pytest
from pydantic import BaseModel


# この起債でtupleになった気がしたが、気のせいだった
class TestTuple:
    @staticmethod
    def method_01(a: str, b: str) -> None:
        print(f"a: {a}, b: {b}")
        print(f"a: {type(a)}, b: {type(b)}")

    def test_01(self):
        TestTuple.method_01("a", "b")

    def test_02(self):
        TestTuple.method_01(
            a="a",
            b="b",
        )