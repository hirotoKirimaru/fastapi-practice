import datetime

from sqlalchemy import Column, Integer, String, Date
from src.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    email = Column(String(1024))
    organization = Column(String(1024))
    birth_day = Column(Date)

    def age(self, now: datetime.date) -> int:
        """
        年齢を計算する.
        """
        return now.year - self.birth_day.year - ((now.month, now.day) < (self.birth_day.month, self.birth_day.day))

