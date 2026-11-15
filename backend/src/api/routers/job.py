from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter

from src.worker.celery_app import celery_app
from src.worker.tasks import create_user_profile

router = APIRouter()


@router.post("/user-profiles/{user_id}")
async def enqueue_user_profile(user_id: int) -> dict[str, Any]:
    """プロフィール作成を worker に投げる。API はすぐ返り、処理は worker が行う"""
    result = create_user_profile.delay(user_id)
    return {"task_id": result.id}


@router.get("/{task_id}")
async def get_job(task_id: str) -> dict[str, Any]:
    result = AsyncResult(task_id, app=celery_app)
    body: dict[str, Any] = {"task_id": task_id, "status": result.status}
    if result.successful():
        body["result"] = result.result
    return body
