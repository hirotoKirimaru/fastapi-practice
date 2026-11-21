import logging
from typing import Any

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException
from fastapi_users.schemas import BaseUserCreate
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import emails
from src.auth.db import SQLModelUserDatabase, revoke_all_tokens
from src.helper.config import settings
from src.models.user import User

logger = logging.getLogger(__name__)

PASSWORD_MIN_LENGTH = 8


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    # パスワード再設定とメール確認のトークン（JWT）の署名鍵。ログインのトークンとは別物
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    @property
    def _session(self) -> AsyncSession:
        assert isinstance(self.user_db, SQLModelUserDatabase)
        return self.user_db.session

    async def validate_password(
        self, password: str, user: BaseUserCreate | User
    ) -> None:
        if len(password) < PASSWORD_MIN_LENGTH:
            raise InvalidPasswordException(
                reason=f"パスワードは {PASSWORD_MIN_LENGTH} 文字以上にしてください"
            )
        if user.email and user.email.split("@")[0].lower() in password.lower():
            raise InvalidPasswordException(
                reason="パスワードにメールアドレスを含めないでください"
            )

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> User | None:
        """BaseUserManager.authenticate と同じ流れに、パスワードを持たないユーザの扱いを足したもの。

        GraphQL の createUser などで作ったユーザは hashed_password が空で、そのまま検証すると
        pwdlib が例外（UnknownHashError）にする。居ない場合と同じく、ハッシュ計算だけして None を返す
        （かかる時間でユーザの有無が漏れないように）
        """
        user = await self.user_db.get_by_email(credentials.username)
        if user is None or not user.hashed_password:
            self.password_helper.hash(credentials.password)
            return None
        verified, updated_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        if updated_hash is not None:  # 古い方式（bcrypt）のハッシュは Argon2 に上げる
            await self.user_db.update(user, {"hashed_password": updated_hash})
        return user

    async def on_after_register(
        self, user: User, request: Request | None = None
    ) -> None:
        logger.info("user registered: id=%s", user.id)

    async def on_after_update(
        self, user: User, update_dict: dict[str, Any], request: Request | None = None
    ) -> None:
        # パスワードが変わったら、他の端末のトークンも全部無効にする
        if "password" in update_dict:
            await revoke_all_tokens(self._session, user)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        emails.send_reset_password(user, token)

    async def on_after_reset_password(
        self, user: User, request: Request | None = None
    ) -> None:
        await revoke_all_tokens(self._session, user)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        emails.send_verify(user, token)
