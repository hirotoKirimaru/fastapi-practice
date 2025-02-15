from typing import Any

import polars
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.api.deps import SessionWriterDep
from src.helper.helper import session_context

router = APIRouter()


@router.get("/files", description="ファイルをダウンロードする")
async def download_files() -> StreamingResponse:
    return StreamingResponse()


@router.put(
    "/files", response_model=bool, description="ユーザ登録用ファイルをアップロードする"
)
async def register_by_users(db: SessionWriterDep, file: UploadFile = File(...)) -> Any:
    async with session_context(db) as _session:
        contents = await file.read()
        try:
            df = polars.read_csv(contents)
            print(df)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"ファイルの読み込みに失敗しました: {e}"
            )
    return True
