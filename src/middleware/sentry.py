import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from src.helper.config import settings


class Sentry:
    @classmethod
    def init_sentry(cls) -> None:
        if not settings.SENTRY_DSN or settings.ENV == "local":
            return

        sentry_sdk.init(
            dsn=str(settings.SENTRY_DSN),
            enable_tracing=True,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
        )
