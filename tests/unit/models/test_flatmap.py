from itertools import chain


def flatten(lst):
    for el in lst:
        if isinstance(el, list):
            yield from flatten(el)
        else:
            yield el


class TestFlatmap:
    async def test_01(self):
        input_ = ["1", ["2", "3"]]

        actual = list(chain.from_iterable(input_))

        assert ["1", "2", "3"] == actual

    async def test_02(self):
        input_ = [1, [2, 3]]

        actual = list(
            chain.from_iterable(
                item if isinstance(item, list) else [item] for item in input_
            )
        )

        assert [1, 2, 3] == actual

    async def test_03(self):
        input_ = [[1], [2, 3]]

        actual = list(chain.from_iterable(input_))

        assert [1, 2, 3] == actual

    async def test_04(self):
        input_ = [1, [2, [3, [4, 5]]]]

        actual = list(flatten(input_))

        assert [1, 2, 3, 4, 5] == actual
