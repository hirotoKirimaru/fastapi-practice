from datetime import datetime

from sqlalchemy import DATETIME, INTEGER, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
from src.models.organization import Organization

from src.helper.datetime_resolver import DatetimeResolver


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    __name: Mapped[str] = mapped_column("name", VARCHAR(1024))
    __email: Mapped[str] = mapped_column("email", VARCHAR(1024))
    soft_destroyed_at: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True)
    organization_id: Mapped[str] = mapped_column(INTEGER, ForeignKey("organizations.id"))
    organization: Mapped["Organization"]  = relationship("Organization")
    organization2: Mapped["Organization"]  = relationship("Organization", lazy="joined") # 自動でロードする
    organization3: Mapped["Organization"]  = relationship("Organization", lazy="noload") # 読み込まない
    organization4: Mapped["Organization"]  = relationship("Organization", lazy="immediate") # 親読み込み時に自動(これが一番早い？)
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

    @hybrid_property
    def name(self) -> str:
        if self.soft_destroyed_at is None:
            return self.__name
        return "削除済ユーザ"

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @name.expression
    def name(cls) -> str:
        return cls.__name

    @hybrid_property
    def email(self) -> str:
        if self.soft_destroyed_at is None:
           return self.__email
        return "削除済みEmail"

    @email.setter
    def email(self, email: str) -> None:
        self.__email = email

    @email.expression
    def email(cls) -> str:
        return cls.__email

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
