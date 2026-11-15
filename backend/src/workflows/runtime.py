"""DBOS（durable workflow）の設定。

DBOS はアプリと同じプロセスで動くライブラリで、ワークフローの進み具合を PostgreSQL に記録する。
記録先（システム DB）はアプリの DB と同じサーバーの `<DB名>_dbos_sys`。無ければ DBOS が作る。

⚠️ uvicorn を複数プロセス（--workers 4 など）で動かすときは、プロセスごとに executor_id を
変えないと、落ちたワークフローの再開を複数プロセスが同時に引き受けてしまう。
"""

from dbos import DBOSConfig
from sqlalchemy import make_url

from src.helper.config import settings

APP_NAME = "fastapi-practice"


def dbos_config(database_url: str | None = None, name: str = APP_NAME) -> DBOSConfig:
    url = make_url(database_url or settings.DATABASE_URL)
    system_url = url.set(database=f"{url.database}_dbos_sys")
    return {
        "name": name,
        "system_database_url": system_url.render_as_string(hide_password=False),
    }
