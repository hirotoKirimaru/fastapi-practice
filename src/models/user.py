from sqlalchemy import Column, Date, ForeignKey, Integer, String

from src.db import Base
from src.helper.datetime_resolver import DatetimeResolver


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    email = Column(String(1024))
    organization_id = Column(String(1024))
    birth_day = Column(Date)

    @property
    def age(self) -> int:
        """
        年齢を計算する.
        """
        now = DatetimeResolver.today()
        return (
            now.year
            - self.birth_day.year
            - ((now.month, now.day) < (self.birth_day.month, self.birth_day.day))
        )

    @property
    def minor(self) -> bool:
        return self.age < 18


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
