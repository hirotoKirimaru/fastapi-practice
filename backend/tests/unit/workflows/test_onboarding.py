"""DBOS の durable workflow が「何度呼んでも 1 回」「失敗したステップは自動で再試行」になることを確かめる"""

import pytest
from dbos import DBOS, SetWorkflowID
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.models.user import User, UserProfile
from src.workflows import onboarding

USER_ID = 9001


@pytest.fixture
async def user(dbos_runtime: async_sessionmaker[AsyncSession]) -> int:
    async with dbos_runtime() as session:
        session.add(User(id=USER_ID, name="dbos", email="dbos@example.com"))
        await session.commit()
    return USER_ID


@pytest.fixture
def notified(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []

    async def fake_notify(user_id: int) -> None:
        calls.append(user_id)

    monkeypatch.setattr(onboarding, "notify", fake_notify)
    return calls


async def _profile_count(
    factory: async_sessionmaker[AsyncSession], user_id: int
) -> int:
    async with factory() as session:
        result = await session.execute(
            select(func.count())
            .select_from(UserProfile)
            .where(UserProfile.user_id == user_id)
        )
        return result.scalar_one()


async def test_same_workflow_id_runs_once(
    dbos_runtime: async_sessionmaker[AsyncSession], user: int, notified: list[int]
) -> None:
    workflow_id = onboarding.onboarding_workflow_id(user)

    with SetWorkflowID(workflow_id):
        first = await onboarding.onboard_user(user)
    # 同じ ID でもう一度呼ぶと、ステップは実行されず記録済みの結果が返る
    with SetWorkflowID(workflow_id):
        second = await onboarding.onboard_user(user)

    assert first == second
    assert await _profile_count(dbos_runtime, user) == 1
    assert notified == [user]

    status = await DBOS.get_workflow_status_async(workflow_id)
    assert status is not None
    assert status.status == "SUCCESS"


async def test_failed_step_is_retried(
    dbos_runtime: async_sessionmaker[AsyncSession],
    user: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts: list[int] = []

    async def flaky_notify(user_id: int) -> None:
        attempts.append(user_id)
        if len(attempts) < 2:
            raise ConnectionError("通知先が一時的に落ちている")

    monkeypatch.setattr(onboarding, "notify", flaky_notify)

    with SetWorkflowID(onboarding.onboarding_workflow_id(user)):
        await onboarding.onboard_user(user)

    # 1 回目の失敗は DBOS がリトライし、プロフィール作成はやり直さない
    assert len(attempts) == 2
    assert await _profile_count(dbos_runtime, user) == 1


async def test_api_starts_workflow_once(
    async_client: AsyncClient,
    dbos_runtime: async_sessionmaker[AsyncSession],
    user: int,
    notified: list[int],
) -> None:
    first = await async_client.post(f"/workflows/onboarding/{user}")
    second = await async_client.post(f"/workflows/onboarding/{user}")
    assert first.status_code == 200
    assert first.json() == second.json() == {"workflow_id": f"onboarding-{user}"}

    handle = await DBOS.retrieve_workflow_async(f"onboarding-{user}")
    await handle.get_result()

    response = await async_client.get(f"/workflows/onboarding-{user}")
    assert response.json() == {"workflow_id": f"onboarding-{user}", "status": "SUCCESS"}
    assert notified == [user]
    assert await _profile_count(dbos_runtime, user) == 1


async def test_unknown_workflow_is_404(
    async_client: AsyncClient, dbos_runtime: async_sessionmaker[AsyncSession]
) -> None:
    response = await async_client.get("/workflows/does-not-exist")
    assert response.status_code == 404
