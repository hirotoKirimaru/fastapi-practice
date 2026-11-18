import secrets
import warnings
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ENV: Literal["local", "staging", "prod"] = "local"
    PROJECT_NAME: str = "fastapi-practice"
    API_V1_STR: str = ""
    # JWT の署名鍵。全プロセスで同じ値でないと、あるプロセスが発行したトークンを別のプロセスが
    # 受け付けない（--workers 4 や再起動で壊れる）。以前は既定値がプロセスごとの乱数だったので、
    # ENV が local 以外で未設定ならエラーにする。local だけは未設定でも乱数で起動する（警告あり）
    SECRET: str = ""
    GOOGLE_API_KEY: str = ""

    # SQLAlchemy の接続先。ドライバは psycopg 3 で、同期・非同期のどちらの engine にも同じ URL を渡せる。
    # 既定値は infra/compose.yml の db サービス（コンテナ内から見た host / port）。
    # ホストから直接つなぐときは postgresql+psycopg://postgres@localhost:35432/demo
    # （ローカル / CI の DB はパスワードなし。本番では環境変数で上書きする）
    DATABASE_URL: str = "postgresql+psycopg://postgres@db:5432/demo"
    # 発行した SQL をすべて標準出力に出す（学習用に既定で有効）。
    # ログレベルとは無関係に出るので、並列テストなど出力を絞りたいときは SQL_ECHO=false にする
    SQL_ECHO: bool = True

    # Celery のブローカーと結果の保存先。既定値は infra/compose.yml の kvs（Valkey。Redis 互換なので redis://）
    CELERY_BROKER_URL: str = "redis://kvs:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://kvs:6379/1"

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    SENTRY_DSN: HttpUrl | None = None

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value in {"changethis", "please-change-me"}:
            message = (
                f'The value of {var_name} is "{value}", '
                "for security, please change it, at least for deployments."
            )
            if self.ENV == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        if not self.SECRET:
            if self.ENV != "local":
                raise ValueError(
                    "SECRET が設定されていません。全プロセスで同じ値を環境変数で渡してください"
                )
            warnings.warn(
                "SECRET が未設定なので乱数を使います。プロセスごとに値が変わるため、"
                "複数プロセスや再起動をまたいでトークンは使えません",
                stacklevel=1,
            )
            self.SECRET = secrets.token_urlsafe(32)
        self._check_default_secret("SECRET", self.SECRET)
        return self


settings = Settings()
