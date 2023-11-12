import pytest
import starlette.status


@pytest.mark.asyncio
async def test_response_json(async_client):
    response = await async_client.get("/health/")
    assert response.status_code == starlette.status.HTTP_200_OK
    assert response.json() == dict(Hello="World")
