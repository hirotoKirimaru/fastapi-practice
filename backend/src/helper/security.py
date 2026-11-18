from datetime import timedelta
from typing import Any

import jwt
from fastapi_users.password import PasswordHelper

from src.helper.config import settings
from src.helper.datetime_resolver import DatetimeResolver

# 認証（fastapi-users。src/auth/）と同じハッシュ方式（Argon2。bcrypt のハッシュも検証できる）。
# 以前は passlib の bcrypt だったが、passlib が bcrypt 4.1 以降と組み合わせられず、
# ハッシュを作れなかった（MissingBackendError）
password_helper = PasswordHelper()


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = DatetimeResolver.now() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    verified, _ = password_helper.verify_and_update(plain_password, hashed_password)
    return verified


def get_password_hash(password: str) -> str:
    return password_helper.hash(password)
