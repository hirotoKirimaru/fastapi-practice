from datetime import date

from src.models.user import User
from src.models.minors import Minors

class TestIterator:
    NOW: date = date(2023, 11, 20)
    def test_one(self, mocker):
        mocker.patch('src.helper.datetime_resolver.DatetimeResolver.today' , return_value=self.NOW)
        base = [
            User(birth_day=date(2003, 11, 20)),
            User(birth_day=date(2003, 11, 20)),
            User(birth_day=date(2003, 11, 20)),
            User(birth_day=date(2003, 11, 20))
                    ]

        target = Minors(base)

        actual = [x for x in target]
        assert len(base) == len(actual)