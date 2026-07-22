from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import DATETIME, VARCHAR, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship
from sqlmodel._compat import SQLModelConfig

from src.helper.datetime_resolver import DatetimeResolver
from src.models.base import Base
from src.models.organization import Organization
from src.models.post import Post

if TYPE_CHECKING:
    from .organization import Organization
    from .post import Post


class User(Base, table=True):
    __tablename__ = "users"

    model_config = SQLModelConfig(ignored_types=(hybrid_property,))

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(VARCHAR(1024)))
    email: str = Field(sa_column=Column(VARCHAR(1024)))
    soft_destroyed_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DATETIME)
    )
    # UTCDateTime型を使うことで取得時にSQLを得られる
    # soft_destroyed_at: Optional[datetime] = Field(
    #     default=None, sa_column=Column(UTCDateTime)
    # )
    organization_id: Optional[int] = Field(default=None, foreign_key="organizations.id")
    organization: Optional["Organization"] = Relationship()
    organization2: Optional["Organization"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    organization3: Optional["Organization"] = Relationship(
        sa_relationship_kwargs={"lazy": "noload"}
    )
    organization4: Optional["Organization"] = Relationship(
        sa_relationship_kwargs={"lazy": "immediate"}
    )
    birth_day: Optional[datetime] = Field(default=None, sa_column=Column(DATETIME))
    salt: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(255)))

    posts: List["Post"] = Relationship()

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
    def _name__setter(self, value: str) -> None:
        self.name = value

    @display_name.inplace.expression
    @classmethod
    def _name_expression(cls) -> Any:
        return cls.name

    @hybrid_property
    def display_email(self) -> str:
        if self.soft_destroyed_at is None:
            return self.email
        return "削除済みEmail"

    @display_email.inplace.setter
    def _email_setter(self, value: str) -> None:
        self.email = value

    @display_email.inplace.expression
    @classmethod
    def _email_expression(cls) -> Any:
        return cls.email


class UserProfile(Base, table=True):
    __tablename__ = "user_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
