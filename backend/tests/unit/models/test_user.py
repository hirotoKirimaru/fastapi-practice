from datetime import date

import pytest
import pytest_mock
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class TestUser:
    @pytest.mark.asyncio
    async def test_get_single(self, db: AsyncSession):
        # Given
        print([x for x in range(10)])
        # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        print(*[x for x in range(10)])
        # 0 1 2 3 4 5 6 7 8 9


class TestAge:
    NOW: date = date(2023, 11, 20)
    # pytest -m specific
    # , marks = pytest.mark.specific

    @pytest.mark.parametrize(
        "input_birth_day, expected_age",
        [
            (pytest.param(date(2023, 11, 20), 0, id="当日")),
            (pytest.param(date(2023, 11, 19), 0, id="前日")),
            (pytest.param(date(2022, 11, 21), 0, id="1年前+1日")),
            (pytest.param(date(2022, 11, 20), 1, id="1年前当日")),
            (pytest.param(date(2022, 11, 19), 1, id="1年前-1日")),
            (pytest.param(date(1992, 2, 4), 31, id="適当な年齢")),
        ],
    )
    def test_one(
        self, input_birth_day: date, expected_age: int, mocker: pytest_mock.mocker
    ):
        mocker.patch(
            "src.helper.datetime_resolver.DatetimeResolver.today", return_value=self.NOW
        )
        assert User(birth_day=input_birth_day).age == expected_age
