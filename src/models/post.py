from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from src.models.base import Base

if TYPE_CHECKING:
    from .user import User

class Post(Base, table=True):
    __tablename__ = 'posts'
    id: int = Field(primary_key=True)
    title: str
    user_id: int = Field(foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="posts")

