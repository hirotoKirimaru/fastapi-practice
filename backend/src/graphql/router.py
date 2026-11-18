from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from src.api.deps import get_writer_db
from src.auth.backend import fastapi_users
from src.graphql.schema import schema
from src.models.user import User

# REST と同じ Authorization: Bearer <token>。無い・不正・ログアウト済みなら None（ログイン不要の
# フィールドはそのまま使え、要ログインのフィールドだけが IsAuthenticated で弾かれる）
optional_active_user = fastapi_users.current_user(active=True, optional=True)


async def get_context(
    session: AsyncSession = Depends(get_writer_db),
    user: User | None = Depends(optional_active_user),
) -> dict[str, Any]:
    return {"session": session, "user": user}


graphql_router: GraphQLRouter[dict[str, Any], Any] = GraphQLRouter(
    schema, context_getter=get_context
)
