
from sqlalchemy import DATETIME, TypeDecorator
from sqlmodel import SQLModel
from typing_extensions import override

from src.helper.datetime_resolver import DatetimeResolver


# class Base(SQLModel, table=True):
class Base(SQLModel):
    def __repr__(self):
        return str(self.__dict__)

    # def __eq__(self)


class UTCDateTime(TypeDecorator):
    impl = DATETIME

    @override
    def process_result_value(self, value, dialect):
        return DatetimeResolver.enforce_utc(value)
