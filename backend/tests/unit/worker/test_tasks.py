"""Celery のタスクを、本物の worker（スレッド・メモリのブローカー）経由で動かして確かめる"""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from src.models.user import UserProfile
from src.worker import tasks

USER_ID = 9101


@pytest.fixture
def user(celery_worker: None) -> int:
    with tasks.engine_factory().begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (id, name, email) VALUES (:id, 'w', 'w@example.com')"
            ),
            {"id": USER_ID},
        )
    return USER_ID


def _profile_count(user_id: int) -> int:
    with Session(tasks.engine_factory()) as session:
        return session.scalar(
            select(func.count())
            .select_from(UserProfile)
            .where(UserProfile.user_id == user_id)
        )


def test_task_runs_on_worker(user: int) -> None:
    result = tasks.create_user_profile.delay(user)
    profile_id = result.get(timeout=10)

    assert result.status == "SUCCESS"
    assert isinstance(profile_id, int)
    assert _profile_count(user) == 1


def test_task_is_safe_to_run_twice(user: int) -> None:
    """acks_late で再配送されることがあるので、2 回実行しても二重にならないこと"""
    first = tasks.create_user_profile.delay(user).get(timeout=10)
    second = tasks.create_user_profile.delay(user).get(timeout=10)

    assert first == second
    assert _profile_count(user) == 1


async def test_api_enqueues_and_reports(async_client: AsyncClient, user: int) -> None:
    response = await async_client.post(f"/jobs/user-profiles/{user}")
    assert response.status_code == 200
    task_id = response.json()["task_id"]

    # worker が処理し終えるまで状態を見る
    for _ in range(100):
        body = (await async_client.get(f"/jobs/{task_id}")).json()
        if body["status"] == "SUCCESS":
            break
        await asyncio.sleep(0.05)

    assert body["status"] == "SUCCESS"
    assert isinstance(body["result"], int)
    assert _profile_count(user) == 1


async def test_unknown_job_is_pending(async_client: AsyncClient) -> None:
    # Celery は存在しないタスク ID と「まだ始まっていない」を区別しない
    response = await async_client.get("/jobs/does-not-exist")
    assert response.json() == {"task_id": "does-not-exist", "status": "PENDING"}
