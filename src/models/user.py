from sqlalchemy import Column, Integer, String
from src.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    email = Column(String(1024))
    organization = Column(String(1024))
