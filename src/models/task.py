# from sqlalchemy import Column, ForeignKey, Integer, String
# from sqlalchemy.orm import relationship
from dataclasses import Field
from typing import Sequence, List

from sqlmodel import Column, Integer, String, ForeignKey, Relationship, Field
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
