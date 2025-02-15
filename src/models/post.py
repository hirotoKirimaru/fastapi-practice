from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.models.base import Base



class Post(Base, table=True):
    __tablename__ = 'posts'
    id: int = Field(primary_key=True)
    title: str
    user_id: int = Field(foreign_key="users.id")
