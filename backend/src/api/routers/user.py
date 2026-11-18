from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi_users import InvalidPasswordException
from sqlalchemy import func
from sqlmodel import col, select

# PEP 810 の遅延 import。CSV を読むエンドポイントが呼ばれるまで polars を読み込まない
lazy import polars

from src.api.deps import SessionWriterDep
from src.auth.backend import CurrentSuperuser, CurrentUser, get_user_manager
from src.auth.manager import UserManager
from src.helper.helper import session_context
from src.models.user import User
from src.schemas.auth import UpdatePassword, UserRead, UsersPage, UserUpdate

router = APIRouter()

# GET/PATCH /users/me と GET/PATCH/DELETE /users/{id}（管理者）は fastapi-users が持つ
# （src/api/main.py）。ここは fastapi-users に無いものだけ。/users/{id} より先に登録すること


@router.get("", response_model=UsersPage, description="ユーザ一覧（管理者のみ）")
async def list_users(
    _: CurrentSuperuser,
    db: SessionWriterDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Any:
    alive = col(User.soft_destroyed_at).is_(None)
    count = (
        await db.execute(select(func.count()).select_from(User).where(alive))
    ).scalar_one()
    users = (
        await db.execute(
            select(User).where(alive).order_by(col(User.id)).offset(skip).limit(limit)
        )
    ).scalars()
    return UsersPage(
        data=[UserRead.model_validate(u, from_attributes=True) for u in users],
        count=count,
    )


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    description="今のパスワードを確かめてから変える。変えると全端末のトークンが無効になる",
)
async def update_password(
    body: UpdatePassword,
    current_user: CurrentUser,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> None:
    verified, _ = user_manager.password_helper.verify_and_update(
        body.current_password, current_user.hashed_password
    )
    if not verified:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="今のパスワードが違います"
        )
    if body.current_password == body.new_password:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="新しいパスワードが今と同じです"
        )
    try:
        await user_manager.update(
            UserUpdate(password=body.new_password), current_user, safe=True
        )
    except InvalidPasswordException as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.reason) from e


@router.delete(
    "/me", status_code=status.HTTP_204_NO_CONTENT, description="退会する（論理削除）"
)
async def delete_me(
    current_user: CurrentUser,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> None:
    if current_user.is_superuser:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="管理者は自分を削除できません"
        )
    await user_manager.delete(current_user)


@router.get("/files", description="ファイルをダウンロードする")
async def download_files() -> StreamingResponse:
    return StreamingResponse(content=iter([]))


@router.put(
    "/files", response_model=bool, description="ユーザ登録用ファイルをアップロードする"
)
async def register_by_users(db: SessionWriterDep, file: UploadFile = File(...)) -> Any:
    async with session_context(db) as _session:
        contents = await file.read()
        try:
            df = polars.read_csv(contents)
            print(df)
        # NOTE: polars が送出する例外は多岐にわたるため、意図的に広く捕捉して 400 に変換する
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"ファイルの読み込みに失敗しました: {e}"
            ) from e
    return True
