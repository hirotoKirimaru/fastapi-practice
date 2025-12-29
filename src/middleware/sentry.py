import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration


class Sentry:
    @classmethod
    def init_sentry(cls) -> None:
        return 
        
        # NOTE: test tomaranai
        _ = sentry_sdk.init(
            dsn="https://41f9f871815cd788ed98b20b44f5b383@o4507057023811584.ingest.us.sentry.io/4507057026498560",
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
        )
