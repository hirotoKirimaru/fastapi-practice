from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

# PEP 810 の遅延 import。CSV を読むエンドポイントが呼ばれるまで polars を読み込まない
lazy import polars

from src.api.deps import CurrentUser, SessionWriterDep
from src.helper.helper import session_context
from src.schemas.auth import UserPublic

router = APIRouter()


@router.get(
    "/me",
    response_model=UserPublic,
    description="ログイン中のユーザ（Authorization: Bearer <token> が必要）",
)
async def read_me(current_user: CurrentUser) -> Any:
    return current_user


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
