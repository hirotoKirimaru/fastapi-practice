from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from src.api.deps import get_db
from src.graphql.schema import schema


async def get_context(session: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    return {"session": session}


graphql_router: GraphQLRouter = GraphQLRouter(schema, context_getter=get_context)
