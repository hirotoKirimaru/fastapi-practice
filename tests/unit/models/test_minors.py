from datetime import date

import pytest_mock

from src.models.minors import Minors
from src.models.user import User


class TestIterator:
    NOW: date = date(2023, 11, 20)

    def test_one(self, mocker: pytest_mock.mocker):
        mocker.patch(
            "src.helper.datetime_resolver.DatetimeResolver.today", return_value=self.NOW
        )

        user_1 = User(birth_day=date(2006, 11, 19))
        user_2 = User(birth_day=date(2006, 11, 20))
        user_3 = User(birth_day=date(2005, 11, 21))
        base = [
            user_1,
            user_2,
            user_3,
            User(birth_day=date(2005, 11, 20)),
            User(birth_day=date(2005, 11, 19)),
            User(birth_day=date(2000, 1, 1)),
        ]

        target = Minors(base)

        actual = [x for x in target]
        assert len(actual) == 3, "18歳以下は3人"
        # assert set(actual) == {user_1, user_2, user_3}
        # NOTE: E TypeError: unhashable type: 'User'
        assert user_1 in actual
        assert user_2 in actual
        assert user_3 in actual

        # target.valueと同じ
        # actual_2 = [x for x in target.value]
        # assert set(actual) == set(actual_2)
        for x in target.value:
            assert x in actual
