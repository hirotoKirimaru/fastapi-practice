from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: Annotated[str | None, Field(None, examples=["クリーニングを取りに行く"])]


class Task(TaskBase):
    id: int
    title: Annotated[str | None, Field(None, examples=["クリーニングを取りに行く"])]
    done: Annotated[bool, Field(False, description="完了フラグ")]

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
