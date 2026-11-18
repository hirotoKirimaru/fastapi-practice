"""認証のシナリオ。REST（/signup, /login/access-token, /users/me）と GraphQL（me, createPost）"""

from datetime import timedelta

import pytest
from starlette import status

from src.helper.security import create_access_token

pytestmark = pytest.mark.anyio

EMAIL = "auth-scenario@example.com"
PASSWORD = "correct-horse-battery"


async def _signup(async_client, email: str = EMAIL, password: str = PASSWORD):
    return await async_client.post(
        "/signup", json={"name": "認証 太郎", "email": email, "password": password}
    )


async def _login(async_client, email: str = EMAIL, password: str = PASSWORD):
    # OAuth2 のパスワードフローなので JSON ではなくフォームで送る
    return await async_client.post(
        "/login/access-token", data={"username": email, "password": password}
    )


async def test_signup_login_and_me(async_client):
    response = await _signup(async_client)
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user["email"] == EMAIL
    # ハッシュは返さない
    assert "hashed_password" not in user

    response = await _login(async_client)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert token["token_type"] == "bearer"

    response = await async_client.get(
        "/users/me", headers={"Authorization": f"Bearer {token['access_token']}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user


async def test_signup_duplicate_email(async_client):
    assert (await _signup(async_client)).status_code == status.HTTP_201_CREATED
    response = await _signup(async_client)
    assert response.status_code == status.HTTP_409_CONFLICT


async def test_signup_short_password(async_client):
    response = await _signup(async_client, password="short")
    # バリデーションエラーはアプリ全体で 400 に揃えている（src/main.py）
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    ("email", "password"),
    [(EMAIL, "wrong-password"), ("nobody@example.com", PASSWORD)],
    ids=["パスワード違い", "未登録"],
)
async def test_login_rejected(async_client, email, password):
    await _signup(async_client)
    response = await _login(async_client, email=email, password=password)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer not-a-jwt"},
        {"Authorization": f"Bearer {create_access_token(1, timedelta(minutes=-1))}"},
        {
            "Authorization": f"Bearer {create_access_token(999_999_999, timedelta(minutes=5))}"
        },
    ],
    ids=["ヘッダ無し", "形式不正", "期限切れ", "存在しないユーザ"],
)
async def test_me_requires_valid_token(async_client, headers):
    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def _graphql(async_client, query: str, token: str | None = None, **variables):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()


async def test_graphql_me_and_create_post(async_client):
    user = (await _signup(async_client)).json()
    token = (await _login(async_client)).json()["access_token"]

    body = await _graphql(async_client, "{ me { id email } }", token)
    assert body == {"data": {"me": {"id": user["id"], "email": EMAIL}}}

    body = await _graphql(
        async_client,
        "mutation ($title: String!) { createPost(title: $title) { title userId } }",
        token,
        title="はじめての投稿",
    )
    assert body == {
        "data": {"createPost": {"title": "はじめての投稿", "userId": user["id"]}}
    }


@pytest.mark.parametrize("token", [None, "not-a-jwt"], ids=["トークン無し", "形式不正"])
async def test_graphql_me_requires_auth(async_client, token):
    body = await _graphql(async_client, "{ me { id } }", token)
    assert body["data"] is None
    assert body["errors"][0]["message"] == "User is not authenticated"

    # ログイン不要のフィールドはトークンが無くても使える
    body = await _graphql(async_client, '{ hello(name: "graphql") }', token)
    assert body == {"data": {"hello": "Hello, graphql!"}}
