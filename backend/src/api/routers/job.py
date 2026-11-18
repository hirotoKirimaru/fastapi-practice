from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter

from src.worker import names
from src.worker.celery_app import celery_app

router = APIRouter()


@router.post("/user-profiles/{user_id}")
async def enqueue_user_profile(user_id: int) -> dict[str, Any]:
    """プロフィール作成を worker に投げる。API はすぐ返り、処理は worker が行う"""
    # タスクの実装は import せず、名前で投入する（API に worker 側の依存を持ち込まない）
    result = celery_app.send_task(names.CREATE_USER_PROFILE, args=[user_id])
    return {"task_id": result.id}


@router.get("/{task_id}")
async def get_job(task_id: str) -> dict[str, Any]:
    result = AsyncResult(task_id, app=celery_app)
    body: dict[str, Any] = {"task_id": task_id, "status": result.status}
    if result.successful():
        body["result"] = result.result
    return body
