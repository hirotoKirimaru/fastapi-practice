import pytest
import pytest_mock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

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
    @pytest.mark.parametrize("input_birth_day, expected_age", [
        (date(2023, 11, 20), 0),
        (date(2023, 11, 19), 0),
        (date(2022, 11, 21), 0),
        (date(2022, 11, 20), 1),
        (date(2022, 11, 19), 1),
        (date(1992, 2, 4), 31)
    ])
    def test_one(self, input_birth_day: date, expected_age: int, mocker: pytest_mock.mocker):
        mocker.patch('src.helper.datetime_resolver.DatetimeResolver.today' , return_value=self.NOW)
        assert User(birth_day=input_birth_day).age == expected_age