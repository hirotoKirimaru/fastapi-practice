from datetime import datetime

from sqlalchemy import DATETIME, INTEGER, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
from src.models.organization import Organization

from src.helper.datetime_resolver import DatetimeResolver


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(1024))
    email: Mapped[str] = mapped_column(VARCHAR(1024))
    organization_id: Mapped[str] = mapped_column(INTEGER, ForeignKey("organizations.id"))
    organization: Mapped["Organization"]  = relationship("Organization")
    birth_day: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True)
    salt: Mapped[str | None] = mapped_column(VARCHAR(255), nullable=True)

    @property
    def age(self) -> int:
        """
        年齢を計算する.
        """
        if self.birth_day is None:
            raise ValueError("ガード条件を満たしていません")
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
