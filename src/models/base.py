import datetime
from typing import Any, override

from sqlalchemy import DATETIME, TypeDecorator
from sqlalchemy.engine import Dialect
from sqlmodel import SQLModel

from src.helper.datetime_resolver import DatetimeResolver


# class Base(SQLModel, table=True):
class Base(SQLModel):
    def __repr__(self) -> str:
        return str(self.__dict__)

    # def __eq__(self)


class UTCDateTime(TypeDecorator[datetime.datetime]):
    impl = DATETIME

    @override
    def process_result_value(
        self, value: Any, dialect: Dialect
    ) -> datetime.datetime | None:
        return DatetimeResolver.enforce_utc(value)
