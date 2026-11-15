from sqlmodel import Field

from src.models.base import Base


class Organization(Base, table=True):
    __tablename__ = "organizations"

    id: int = Field(primary_key=True)
