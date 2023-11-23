from typing import List, Iterable

from src.models.user import User


class Minors:
    """
    未成年者のまとまり, みたいなのを表現したい.
    """

    value: List[User]

    def __init__(self, value: List[User]):
        self.value = [x for x in value if x.minor]

    def __iter__(self) -> Iterable[User]:
        # イテレータプロトコルを実装する
        return iter(self.value)

    # def __iter__(self):
    #     """
    #     18歳未満のiteratorを作成する.
    #     """
    #     for x in self.value:
    #         yield x if x.age < 18
    #     yield x for x in self.value if x.age < 18
