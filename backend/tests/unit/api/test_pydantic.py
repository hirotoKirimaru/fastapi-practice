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

        result = timeit.timeit(
            lambda: client.get("/pydantic/pydantic_only"), number=1000
        )
        print(result)
        print(f"Pydantic v2: {result:.4f}秒 (1000回のリクエスト)")

    def test_pydantic_with_orjson_response(self):
        response = client.get("/pydantic/pydantic_with_orjson")
        assert response.status_code == 200

        result = timeit.timeit(
            lambda: client.get("/pydantic/pydantic_with_orjson"), number=1000
        )
        print(result)
        print(f"ORJSONResponse: {result:.4f}秒 (1000回のリクエスト)")


# 速度比較（上）はスキップしているので、2 つのパスが同じ JSON を 200 で返すことだけは毎回見る。
# 以前 /pydantic_with_orjson は orjson が依存に無いのに ORJSONResponse を返していて、常に 500 だった
@pytest.mark.parametrize("path", ["pydantic_only", "pydantic_with_orjson"])
def test_responses_are_ok(path: str) -> None:
    response = client.get(f"/pydantic/{path}")
    assert response.status_code == 200
    assert response.json()["login"] == "octocat"
