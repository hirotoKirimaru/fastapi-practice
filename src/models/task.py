from sqlmodel import Relationship, Field
from src.models.base import Base


class Task(Base, table=True):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True)
    title: str = Field(max_length=1024)

    # done: Sequence["Done"] = Relationship(back_populates="task")
    done: "Done" = Relationship(
        back_populates="task",
        cascade_delete=True,
        sa_relationship_kwargs={"uselist": False},
    )


class Done(Base, table=True):
    __tablename__ = "dones"

    # id: int = Field(foreign_key="tasks.id", primary_key=True)
    # NOTE: ondelete を付与しておくと、アプリを経由せずに削除されたデータも安全に処理できる。
    # id: int = Field(foreign_key="tasks.id", primary_key=True, ondelete="RESTRICT")
    id: int = Field(foreign_key="tasks.id", primary_key=True, ondelete="CASCADE")
    # task_id: int = Field()
    # task: Sequence["Task"] = Relationship(back_populates="done")
    task: "Task" = Relationship(back_populates="done")
