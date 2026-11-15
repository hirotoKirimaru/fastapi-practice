from typing import Any

import polars
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.api.deps import SessionWriterDep
from src.helper.helper import session_context

router = APIRouter()


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
