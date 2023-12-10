from sqlalchemy import Column, Integer, String, Date

from src.helper.datetime_resolver import DatetimeResolver
from src.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
