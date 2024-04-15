import base64
import hashlib
from typing import Final

import pyotp

SECRET: Final[str] = "SECRET"


class Totp:
    """
    認証方式のTOTPの処理をまとめたもの.
    類似としてHOTPがある.
    """

    @classmethod
    async def verify(cls, code: str):
        totp = await cls.build_totp_instance(SECRET)
        return totp.verify(code)

    @classmethod
    async def build_totp_instance(cls, secret: str):
        return pyotp.TOTP(secret)

    @classmethod
    async def build_secret(cls, salt: str) -> str:
        secret_base: str = f"{SECRET}"
        hash_: bytes = (
            hashlib.sha256(secret_base.encode("utf-8")).hexdigest().encode("utf-8")
        )
        secret: str = base64.b32encode(hash_).decode("utf-8")
        secret = secret.replace("=", "")
        return secret

    @classmethod
    async def create_salt(cls) -> str:
        return pyotp.random_base32()

    @classmethod
    async def create_totp_url(cls) -> str:
        totp = await cls.build_totp_instance(secret=SECRET)
        return totp.provisioning_uri(name="表示名", issuer_name="きり丸")
