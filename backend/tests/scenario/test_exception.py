import pytest
from httpx import AsyncClient

# import logging


class TestException:
    @pytest.mark.skip
    async def test_01(self, async_client: AsyncClient) -> None:
        body = {"age": 19}
        response = await async_client.put("/exception/exception", json=body)
        assert response.status_code == 500
        assert response.json()["detail"] == "SystemError"

    async def test_02(self, async_client: AsyncClient) -> None:
        body = {"age": 10}
        response = await async_client.put("/exception/exception", json=body)
        assert response.status_code == 400
        assert response.json()["detail"] == "BadRequestException"
