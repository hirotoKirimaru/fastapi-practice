from typing import Any

from dbos import DBOS, SetWorkflowID
from fastapi import APIRouter, HTTPException

from src.workflows.onboarding import onboard_user, onboarding_workflow_id

router = APIRouter()


@router.post("/onboarding/{user_id}")
async def start_onboarding(user_id: int) -> dict[str, Any]:
    """オンボーディングを開始する。同じユーザーで何度呼んでも実行は 1 回だけ"""
    with SetWorkflowID(onboarding_workflow_id(user_id)):
        handle = await DBOS.start_workflow_async(onboard_user, user_id)
    return {"workflow_id": handle.workflow_id}


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> dict[str, Any]:
    status = await DBOS.get_workflow_status_async(workflow_id)
    if status is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    return {"workflow_id": workflow_id, "status": status.status}
