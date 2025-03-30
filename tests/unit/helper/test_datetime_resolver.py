from datetime import datetime
from zoneinfo import ZoneInfo

from src.helper.datetime_resolver import DatetimeResolver


class TestDateTimeResolver:
    class TestIsChronological:
        date_1 = datetime(2022, 1, 1, 12, 0, 0)
        date_2 = datetime(2022, 1, 2, 12, 0, 0)
        date_3 = datetime(2022, 1, 3, 12, 0, 0)

        def test_is_valid_case(self):
            result = DatetimeResolver.is_chronological(self.date_1, self.date_2, self.date_3)
            assert result

        def test_is_invalid_case(self):
            result = DatetimeResolver.is_chronological(self.date_3, self.date_2, self.date_1)
            assert not result

        def test_is_identical_dates(self):
            result = DatetimeResolver.is_chronological(self.date_1, self.date_1)
            assert not result

        def test_ignore_none_is_true(self):
            result = DatetimeResolver.is_chronological(self.date_1, None, self.date_2)
            assert result

        def test_one_value(self):
            result = DatetimeResolver.is_chronological(self.date_1)
            assert result

        # TZのテスト
        # can't compare offset-naive and offset-aware datetimes
        def test_is_chronological_with_tz(self) -> None:
            date_1 = datetime(2022, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            date_2 = datetime(2022, 1, 2, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            date_3 = datetime(2022, 1, 3, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            assert DatetimeResolver.is_chronological(date_1, date_2, date_3)

        def test_mixed_tz_and_not_tz(self) -> None:
            """
            TZありと無しが混在している場合には、UTCとして比較できること
            """
            date_1 = datetime(2022, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            date_2 = datetime(2022, 1, 2, 12, 0, 0)
            date_3 = datetime(2022, 1, 3, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            assert DatetimeResolver.is_chronological(date_1, date_2, date_3)

        def test_mixed_tz(self) -> None:
            """
            TZを考慮して比較できること
            """
            # UTCでは11時
            date_1 = datetime(2022, 1, 2, 20, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
            date_2 = datetime(2022, 1, 2, 12, 0, 0)
            date_3 = datetime(2022, 1, 2, 13, 0, 0, tzinfo=ZoneInfo("UTC"))
            assert DatetimeResolver.is_chronological(date_1, date_2, date_3)

            # UTCでは12時
            date_1 = datetime(2022, 1, 2, 21, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
            assert not DatetimeResolver.is_chronological(date_1, date_2, date_3)