from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlmodel import Field

from src.helper.datetime_resolver import DatetimeResolver
from src.models.base import Base


class AccessToken(Base, table=True):
    """ログイン中のトークン（fastapi-users の DatabaseStrategy）。

    JWT と違って DB に持つので、ログアウト・パスワード変更・退会で即座に無効にできる
    """

    __tablename__ = "access_tokens"

    token: str = Field(sa_column=Column(String(64), primary_key=True))
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    created_at: datetime = Field(
        default_factory=DatetimeResolver.now,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
