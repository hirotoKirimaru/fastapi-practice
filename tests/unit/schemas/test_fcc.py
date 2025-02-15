from typing import List

from pydantic import BaseModel


class Error(BaseModel):
    reason: str
    indexes: List[int] = []


# TODO: こんなことしなくてもいいらしい
class NonEmptyList(list):
    def extend(self, iterable):
        if not iterable:
            return
        super().extend(iterable)


class TestNonEmptyList:
    async def test_01(self):
        error_lists: List[Error] = []
        error_lists.extend([Error(reason="A", indexes=[1, 2, 3]), Error(reason="B")])
        error_lists.extend([])
        error_lists.extend([Error(reason="C")])
        # [Error(reason='A', indexes=[1, 2, 3]), Error(reason='B', indexes=[]), Error(reason='C', indexes=[])]
