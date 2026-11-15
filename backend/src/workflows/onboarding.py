"""ユーザー登録後のオンボーディングを DBOS のワークフローで書いたサンプル。

ワークフローは「プロフィールを作る」→「ようこそ通知を送る」の 2 ステップ。
- 各ステップが終わるたびに結果が DBOS のシステム DB に記録される。途中でプロセスが落ちても、
  再起動後は終わったステップを記録から再生し、続きから再開する（プロフィールが二重にできない）。
- 同じワークフロー ID で何度呼んでも 1 回しか実行されない。API は `onboarding-<user_id>` を使う。
- 通知は外部サービスを想定して失敗時に自動リトライする。

ワークフロー関数の中では DB や外部 API を直接触らず、副作用は必ず @DBOS.step() に置く
（再開時にワークフロー関数は最初から再生されるため）。
"""

from collections.abc import Awaitable, Callable

from dbos import DBOS
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import col

from src.api import deps
from src.models.user import UserProfile

# ステップが使う DB セッション。テストではテスト用 DB に向けて差し替える
session_factory: async_sessionmaker[AsyncSession] = deps.async_session


async def _log_welcome(user_id: int) -> None:
    DBOS.logger.info(f"welcome notification sent to user {user_id}")


# ようこそ通知の送り先。本来はメールや Slack。テストでは差し替えて呼ばれた回数を数える
notify: Callable[[int], Awaitable[None]] = _log_welcome


@DBOS.step()
async def create_profile(user_id: int) -> int:
    async with session_factory() as session:
        found = await session.execute(
            select(UserProfile).where(col(UserProfile.user_id) == user_id)
        )
        if (profile := found.scalars().first()) is None:
            profile = UserProfile(user_id=user_id)
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
        assert profile.id is not None
        return profile.id


@DBOS.step(retries_allowed=True, max_attempts=3, interval_seconds=0.1)
async def send_welcome(user_id: int) -> None:
    await notify(user_id)


@DBOS.workflow()
async def onboard_user(user_id: int) -> int:
    profile_id = await create_profile(user_id)
    await send_welcome(user_id)
    return profile_id


def onboarding_workflow_id(user_id: int) -> str:
    return f"onboarding-{user_id}"
