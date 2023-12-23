import json

from httpx import AsyncClient
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

# import logging
from src.models.user import User


class TestException:
    @pytest.mark.skip
    async def test_01(self, async_client: AsyncClient) -> None:
        body = { "age": 19 }
        response = await async_client.put("/exception/exception", json=body)
        assert response.status_code == 500
        assert response.json()['detail'] == "SystemError"

    async def test_02(self, async_client: AsyncClient) -> None:
        body = { "age": 10 }
        response = await async_client.put("/exception/exception", json=body)
        assert response.status_code == 400
        assert response.json()['detail'] == "BadRequestException"