"""fastapi-users の入出力スキーマに、このアプリの項目（name）を足したもの"""

from fastapi_users import schemas
from pydantic import BaseModel, Field


class UserRead(schemas.BaseUser[int]):
    name: str | None = None


class UserCreate(schemas.BaseUserCreate):
    name: str = Field(min_length=1, max_length=255)


class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class UpdatePassword(BaseModel):
    """PATCH /users/me/password。今のパスワードを確かめてから変える"""

    current_password: str
    new_password: str


class UsersPage(BaseModel):
    data: list[UserRead]
    count: int
