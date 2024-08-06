from datetime import datetime

# from sqlalchemy import DATETIME, INTEGER, VARCHAR, Column, ForeignKey, Integer
# from sqlalchemy.ext.hybrid import hybrid_property
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy.orm.attributes import InstrumentedAttribute
from src.models.base import Base
from src.models.organization import Organization
from sqlalchemy import VARCHAR, DATETIME, ForeignKey

from src.helper.datetime_resolver import DatetimeResolver

from sqlmodel import Field


# class User(Base, table=True):
#     __tablename__ = "users"
#
#     id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
#     __name: Mapped[str] = mapped_column("name", VARCHAR(1024))
#     __email: Mapped[str] = mapped_column("email", VARCHAR(1024))
#     soft_destroyed_at: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True)
#     organization_id: Mapped[str] = mapped_column(
#         INTEGER, ForeignKey("organizations.id")
#     )
#     organization: Mapped["Organization"] = relationship("Organization")
#     organization2: Mapped["Organization"] = relationship(
#         "Organization", lazy="joined"
#     )  # 自動でロードする
#     organization3: Mapped["Organization"] = relationship(
#         "Organization", lazy="noload"
#     )  # 読み込まない
#     organization4: Mapped["Organization"] = relationship(
#         "Organization", lazy="immediate"
#     )  # 親読み込み時に自動(これが一番早い？)
#     birth_day: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True)
#     salt: Mapped[str | None] = mapped_column(VARCHAR(255), nullable=True)
#
#     @property
#     def age(self) -> int:
#         """
#         年齢を計算する.
#         """
#         if self.birth_day is None:
#             raise ValueError("ガード条件を満たしていません")
#         now = DatetimeResolver.today()
#         return (
#             now.year
#             - self.birth_day.year
#             - ((now.month, now.day) < (self.birth_day.month, self.birth_day.day))
#         )
#
#     @property
#     def minor(self) -> bool:
#         return self.age < 18
#
#     @hybrid_property
#     def name(self) -> str:
#         if self.soft_destroyed_at is None:
#             return self.__name
#         return "削除済ユーザ"
#
#     @name.inplace.setter
#     def _name__setter(self, name: str) -> None:
#         self.__name = name
#
#     @name.inplace.expression
#     @classmethod
#     def _name_expression(cls) -> InstrumentedAttribute[str]:
#         return cls.__name
#
#     @hybrid_property
#     def email(self) -> str:
#         if self.soft_destroyed_at is None:
#             return self.__email
#         return "削除済みEmail"
#
#     @email.setter
#     def email(self, email: str) -> None:
#         self.__email = email
#
#     @email.expression
#     def email(cls) -> str:
#         return cls.__email
#
#
# class UserProfile(Base, table=True):
#     __tablename__ = "user_profiles"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))


from typing import Optional, ClassVar
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=VARCHAR(1024))
    email: str = Field(sa_column=VARCHAR(1024))
    soft_destroyed_at: Optional[datetime] = Field(default=None, sa_column=DATETIME)
    organization_id: Optional[int] = Field(default=None, foreign_key="organizations.id")
    organization: Optional["Organization"] = Relationship()
    organization2: Optional["Organization"] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    organization3: Optional["Organization"] = Relationship(sa_relationship_kwargs={"lazy": "noload"})
    organization4: Optional["Organization"] = Relationship(sa_relationship_kwargs={"lazy": "immediate"})
    birth_day: Optional[datetime] = Field(default=None, sa_column=DATETIME)
    salt: Optional[str] = Field(default=None, sa_column=VARCHAR(255))

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
    def display_name(self) -> str:
        if self.soft_destroyed_at is None:
            return self.name
        return "削除済ユーザ"

    @display_name.inplace.setter
    def _name__setter(self, name: str) -> None:
        self.name = name

    @display_name.inplace.expression
    @classmethod
    def _name_expression(cls):
        return cls.name

    @hybrid_property
    def display_email(self) -> str:
        if self.soft_destroyed_at is None:
            return self.email
        return "削除済みEmail"

    @display_email.setter
    def display_email(self, email: str) -> None:
        self.email = email

    @display_email.expression
    def display_email(cls):
        return cls.email

    # pydanticへのフィールド無視設定
    display_name: ClassVar = hybrid_property(display_name)
    display_email: ClassVar = hybrid_property(display_email)

class UserProfile(Base, table=True):
    __tablename__ = "user_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")