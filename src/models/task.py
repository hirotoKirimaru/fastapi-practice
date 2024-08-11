from typing import List

from sqlmodel import Relationship, Field
from src.models.base import Base


class Task(Base, table=True):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True)
    title: str = Field(max_length=1024)

    # done: Sequence["Done"] = Relationship(back_populates="task")
    done: List["Done"] = Relationship(back_populates="task")


class Done(Base, table=True):
    __tablename__ = "dones"

    id: int = Field(foreign_key="tasks.id", primary_key=True)
    # task_id: int = Field()
    # task: Sequence["Task"] = Relationship(back_populates="done")
    task: List["Task"] = Relationship(back_populates="done")
