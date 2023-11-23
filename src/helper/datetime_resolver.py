from datetime import datetime

import pytz

class DatetimeResolver:
    @staticmethod
    def now(timezone: str = "JST") -> datetime:
        return datetime.now(pytz.timezone(timezone))

    @staticmethod
    def today(timezone: str = "JST") -> datetime:
        return datetime.now().astimezone(pytz.timezone(timezone))
