from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    """OAuth2 のパスワードフローで返すアクセストークン"""

    access_token: str
    token_type: str = "bearer"


class UserSignup(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    """外に返してよいユーザの項目（パスワードのハッシュは含めない）"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
