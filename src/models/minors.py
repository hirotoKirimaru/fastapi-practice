from collections.abc import Iterator

from src.models.user import User


class Minors:
    """
    未成年者のまとまり, みたいなのを表現したい.
    """

    value: list[User]

    def __init__(self, value: list[User]):
        self.value = [x for x in value if x.minor]

    def __iter__(self) -> Iterator[User]:
        # イテレータプロトコルを実装する
        # return iter(self.value)
        # こっちでも返却できる
        yield from self.value
        # NOTE: こうしていい感じに返却したいんだが…nextも実装しないと
        # yield self.value
        # NOTE: この挙動も確認
        # yield from self.__dict__.items()

    # def __iter__(self):
    #     """
    #     18歳未満のiteratorを作成する.
    #     """
    #     for x in self.value:
    #         yield x if x.age < 18
    #     yield x for x in self.value if x.age < 18
