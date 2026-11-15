"""テストの DB は本番と同じ PostgreSQL を使い、スキーマは alembic のマイグレーションで作る。

- テスト用 DB は DATABASE_URL の DB 名に `_test` を付けたもの（`TEST_DATABASE_URL` で上書き可）。
  テストセッションの最初に作り直して `alembic upgrade head` し、最後に消す。
  モデルから create_all しないので、モデルとマイグレーションのずれはテストで落ちる。
- 各テストは 1 つの接続上のトランザクションの中で動き、終わったらロールバックする。
  テスト内の commit は SAVEPOINT の解放になるだけなので、テスト同士は干渉しない。
- ローカルでは先に DB を起動しておく: docker compose -f infra/compose.yml up -d --wait db
"""

import os
from collections.abc import AsyncGenerator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL, create_engine, make_url, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command
from src.api.deps import get_db, get_reader_db, get_writer_db
from src.helper.config import settings
from src.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _test_database_url() -> URL:
    if url := os.environ.get("TEST_DATABASE_URL"):
        return make_url(url)
    url = make_url(settings.DATABASE_URL)
    return url.set(database=f"{url.database}_test")


def _recreate_database(url: URL) -> None:
    # CREATE / DROP DATABASE はトランザクションの外でしか実行できないので AUTOCOMMIT で、
    # 対象とは別の DB（postgres）につないで行う
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    try:
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    except OperationalError as e:
        pytest.exit(
            f"テスト用の PostgreSQL（{url.render_as_string()}）につながりません。"
            "ローカルでは `docker compose -f infra/compose.yml up -d --wait db` で起動し、"
            "backend/.env の DATABASE_URL をホスト向け（localhost:35432）にしてください。"
            f"\n{e}",
            returncode=1,
        )
    finally:
        admin.dispose()


def _drop_database(url: URL) -> None:
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture(scope="session")
def migrated_database_url() -> Iterator[URL]:
    """テスト用 DB を作り直し、マイグレーションを当てた URL を返す（DB を使うテストがあるときだけ動く）"""
    url = _test_database_url()
    _recreate_database(url)

    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", url.render_as_string(hide_password=False)
    )
    command.upgrade(alembic_cfg, "head")

    yield url

    _drop_database(url)


@pytest_asyncio.fixture
async def db(migrated_database_url: URL) -> AsyncGenerator[AsyncSession]:
    """テストごとにロールバックされるセッション"""
    engine = create_async_engine(migrated_database_url, poolclass=NullPool)
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(
            bind=conn, autoflush=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """アプリの DB 依存をテスト用セッションに差し替えた HTTP クライアント"""

    async def get_test_db() -> AsyncGenerator[AsyncSession]:
        yield db

    for dependency in (get_db, get_reader_db, get_writer_db):
        app.dependency_overrides[dependency] = get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


# anyio で asyncio だけでテストする
@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
