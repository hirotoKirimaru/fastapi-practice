import timeit

import pytest
from fastapi.testclient import TestClient
from src.main import app  # 上記コードが保存されているファイル名

client = TestClient(app)


# 別にこのレベルだと早くならない…
@pytest.mark.skip
class TestSpeedPydantic:
    def test_pydantic_only_response(self):
        response = client.get("/pydantic/pydantic_only")
        assert response.status_code == 200

        result = timeit.timeit(lambda: client.get("/pydantic/pydantic_only"),
                      number=1000)
        print(result)
        print(f"Pydantic v2: {result:.4f}秒 (1000回のリクエスト)")


    def test_pydantic_with_orjson_response(self):
        response = client.get("/pydantic/pydantic_with_orjson")
        assert response.status_code == 200

        result = timeit.timeit(lambda: client.get("/pydantic/pydantic_with_orjson"),
                      number=1000)
        print(result)
        print(f"ORJSONResponse: {result:.4f}秒 (1000回のリクエスト)")
