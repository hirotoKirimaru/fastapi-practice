from datetime import datetime
from zoneinfo import ZoneInfo


class DatetimeResolver:
    @staticmethod
    def now(timezone: ZoneInfo = ZoneInfo("Asia/Tokyo")) -> datetime:
        return datetime.now(tz=timezone)

    @staticmethod
    def today(timezone: ZoneInfo = ZoneInfo("Asia/Tokyo")) -> datetime:
        return datetime.now().astimezone(tz=timezone)
