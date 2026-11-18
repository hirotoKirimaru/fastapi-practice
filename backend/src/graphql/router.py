from typing import Any

from fastapi import Depends
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from strawberry.fastapi import GraphQLRouter

from src.api.deps import get_db, get_user_from_token
from src.graphql.schema import schema


async def get_context(
    request: Request, session: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    # REST と同じ Authorization: Bearer <JWT>。無い・不正なら user は None（ログイン不要の
    # フィールドはそのまま使え、要ログインのフィールドだけが IsAuthenticated で弾かれる）
    scheme, token = get_authorization_scheme_param(request.headers.get("Authorization"))
    user = await get_user_from_token(
        session, token if scheme.lower() == "bearer" else None
    )
    return {"session": session, "user": user}


graphql_router: GraphQLRouter[dict[str, Any], Any] = GraphQLRouter(
    schema, context_getter=get_context
)
