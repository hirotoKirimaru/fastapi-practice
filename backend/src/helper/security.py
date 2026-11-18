from datetime import timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from src.helper.config import settings
from src.helper.datetime_resolver import DatetimeResolver

# 推奨設定（Argon2id）。以前は passlib の bcrypt だったが、passlib が bcrypt 4.1 以降と
# 組み合わせられず、ハッシュを作れなかった（MissingBackendError）
password_hash = PasswordHash.recommended()


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = DatetimeResolver.now() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> str | None:
    """トークンを検証して sub（ユーザ ID）を返す。署名・期限・形式のどれかが不正なら None"""
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
