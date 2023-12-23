from httpx import AsyncClient
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

# import logging
from src.models.user import User


class TestException:

    async def test_01(self, async_client: AsyncClient) -> None:
        _ = await async_client.put("/exception/exception")
        # assert response.status_code == starlette.status.HTTP_200_OK
        # assert response.json() == dict(Hello="World")