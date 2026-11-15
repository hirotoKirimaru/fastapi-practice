from datetime import datetime
from itertools import pairwise
from zoneinfo import ZoneInfo

# NOTE: ZoneInfo(...) を引数のデフォルト値に直接書くと、呼び出しのたびではなく
# 関数定義時に一度だけ評価される（ruff B008）。モジュールレベルの定数にして
# 意図を明示する。ZoneInfo はイミュータブルなので共有して問題ない。
_JST = ZoneInfo("Asia/Tokyo")
_UTC = ZoneInfo("UTC")


class DatetimeResolver:
    @staticmethod
    def now(timezone: ZoneInfo = _JST) -> datetime:
        return datetime.now(tz=timezone)

    @staticmethod
    def today(timezone: ZoneInfo = _JST) -> datetime:
        return datetime.now(tz=timezone)

    @staticmethod
    def enforce_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=_UTC)
        return value.astimezone(tz=_UTC)

    @staticmethod
    def is_chronological(*dates: datetime | None, inclusive: bool = False) -> bool:
        """
        複数のパラメータのdatetimeが時系列通りであることをチェックする。
        時系列チェックなので、パラメータの順番が重要となる。

        また、呼出元が楽になるように、None項目はすべて除外する。
        """
        safe_dates: list[datetime] = [
            d.astimezone(_UTC) for d in dates if d is not None
        ]

        if inclusive:
            return all(earlier <= later for earlier, later in pairwise(safe_dates))
        else:
            return all(earlier < later for earlier, later in pairwise(safe_dates))
