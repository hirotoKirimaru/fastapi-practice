from datetime import datetime
from zoneinfo import ZoneInfo


class DatetimeResolver:
    @staticmethod
    def now(timezone: ZoneInfo = ZoneInfo("Asia/Tokyo")) -> datetime:
        return datetime.now(tz=timezone)

    @staticmethod
    def today(timezone: ZoneInfo = ZoneInfo("Asia/Tokyo")) -> datetime:
        return datetime.now().astimezone(tz=timezone)

    @staticmethod
    def enforce_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        return value.astimezone(tz=ZoneInfo("UTC"))

    @staticmethod
    def is_chronological(*dates: datetime | None, inclusive: bool = False) -> bool:
        """
        複数のパラメータのdatetimeが時系列通りであることをチェックする。
        時系列チェックなので、パラメータの順番が重要となる。

        また、呼出元が楽になるように、None項目はすべて除外する。
        """
        safe_dates: list[datetime] = [
            d.astimezone(ZoneInfo("UTC")) for d in dates if d is not None
        ]

        if inclusive:
            return all(
                earlier <= later for earlier, later in zip(safe_dates, safe_dates[1:])
            )
        else:
            return all(
                earlier < later for earlier, later in zip(safe_dates, safe_dates[1:])
            )
