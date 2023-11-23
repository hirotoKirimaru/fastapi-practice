import datetime
from typing import List

from src.models import user
class Minors:
    """
    未成年者のまとまり, みたいなのを表現したい.
    ガード条件を優先したほうが本当はいいと思う。
    """
    value: List[user]

    def __repr__(self):
        """
        18歳未満のiteratorを作成する.
        """
        now = datetime.date.today()
        return [x for x in self.value if x.age(now) < 18]