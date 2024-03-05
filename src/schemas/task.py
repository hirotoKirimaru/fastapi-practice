from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    title: Optional[str] = Field(None, examples=["クリーニングを取りに行く"])


class Task(TaskBase):
    id: int
    title: Optional[str] = Field(None, examples=["クリーニングを取りに行く"])
    done: bool = Field(False, description="完了フラグ")

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
