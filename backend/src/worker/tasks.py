"""Celery のタスク。

Celery のタスクは同期関数で書く（prefork の各プロセスで動く）。DB は同期の engine を使い、
fork 後のプロセスで初めて作るように遅延生成する（fork 前に作った接続を子プロセスで共有しない）。
"""

from collections.abc import Callable
from functools import cache

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session
from sqlmodel import col

from src.helper.config import settings
from src.models.user import UserProfile
from src.worker.celery_app import celery_app


@cache
def _default_engine() -> Engine:
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


# テストではテスト用 DB の engine に差し替える
engine_factory: Callable[[], Engine] = _default_engine


@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    max_retries=3,
)
def create_user_profile(self, user_id: int) -> int:  # type: ignore[no-untyped-def]
    """ユーザーのプロフィールを作る。既にあれば作らずにその ID を返す（再配送されても二重にならない）"""
    with Session(engine_factory()) as session:
        profile = session.scalars(
            select(UserProfile).where(col(UserProfile.user_id) == user_id)
        ).first()
        if profile is None:
            profile = UserProfile(user_id=user_id)
            session.add(profile)
            session.commit()
            session.refresh(profile)
        assert profile.id is not None
        return profile.id
