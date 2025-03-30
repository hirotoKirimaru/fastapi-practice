from datetime import timezone

from sqlalchemy import DateTime, TypeDecorator
from sqlmodel import SQLModel


# class Base(SQLModel, table=True):
class Base(SQLModel):
    def __repr__(self):
        return str(self.__dict__)

    # def __eq__(self)


class UTCDateTime(TypeDecorator):
    impl = DateTime

    def process_result_value(self, value, dialect):
        # 取得時にUTCとして返す
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
