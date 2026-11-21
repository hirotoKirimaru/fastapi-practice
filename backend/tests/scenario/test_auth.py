"""認証・ユーザ管理のシナリオ（fastapi-users + src/auth/）。REST と GraphQL の両方"""

import pytest
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy import select, update
from starlette import status

from src.auth import emails
from src.models.access_token import AccessToken
from src.models.user import User

pytestmark = pytest.mark.anyio

PASSWORD = "correct-horse-battery"


class Api:
    """テスト用の小さなクライアント。トークンを持ち回る"""

    def __init__(self, client, token: str | None = None) -> None:
        self.client = client
        self.token = token

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    async def request(self, method: str, url: str, **kwargs):
        return await self.client.request(method, url, headers=self.headers, **kwargs)

    async def graphql(self, query: str, **variables):
        response = await self.request(
            "POST", "/graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == status.HTTP_200_OK
        return response.json()


async def register(
    client, email: str, password: str = PASSWORD, name: str = "認証 太郎"
):
    return await client.post(
        "/auth/register", json={"name": name, "email": email, "password": password}
    )


async def login(client, email: str, password: str = PASSWORD):
    # OAuth2 のパスワードフローなので JSON ではなくフォームで送る
    return await client.post(
        "/auth/login", data={"username": email, "password": password}
    )


async def signed_in(client, email: str, **kwargs) -> tuple[Api, dict]:
    user = (await register(client, email, **kwargs)).json()
    token = (await login(client, email)).json()["access_token"]
    return Api(client, token), user


async def make_superuser(db, user_id: int) -> None:
    await db.execute(update(User).where(User.id == user_id).values(is_superuser=True))
    await db.commit()


# ---------------------------------------------------------------- 登録・ログイン


async def test_register_login_me(async_client):
    response = await register(async_client, "taro@example.com")
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user | {"id": 0} == {
        "id": 0,
        "name": "認証 太郎",
        "email": "taro@example.com",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }

    response = await login(async_client, "taro@example.com")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token_type"] == "bearer"

    api = Api(async_client, response.json()["access_token"])
    assert (await api.request("GET", "/users/me")).json() == user


async def test_register_cannot_become_superuser(async_client):
    # 登録時に is_superuser などを送っても無視される（fastapi-users の safe な作成）
    response = await async_client.post(
        "/auth/register",
        json={
            "name": "x",
            "email": "evil@example.com",
            "password": PASSWORD,
            "is_superuser": True,
        },
    )
    assert response.json()["is_superuser"] is False


@pytest.mark.parametrize(
    ("email", "password", "detail"),
    [
        ("dup@example.com", PASSWORD, "REGISTER_USER_ALREADY_EXISTS"),
        (
            "DUP@example.com",
            PASSWORD,
            "REGISTER_USER_ALREADY_EXISTS",
        ),  # 大文字小文字は区別しない
        ("new@example.com", "short", "REGISTER_INVALID_PASSWORD"),
        (
            "someone@example.com",
            "someone-1234",
            "REGISTER_INVALID_PASSWORD",
        ),  # メールアドレスを含む
    ],
    ids=["重複", "重複（大文字）", "短い", "メールアドレスを含む"],
)
async def test_register_rejected(async_client, email, password, detail):
    await register(async_client, "dup@example.com")
    response = await register(async_client, email, password)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()["detail"]
    assert (body if isinstance(body, str) else body["code"]) == detail


@pytest.mark.parametrize(
    ("email", "password"),
    [("taro@example.com", "wrong-password"), ("nobody@example.com", PASSWORD)],
    ids=["パスワード違い", "未登録"],
)
async def test_login_rejected(async_client, email, password):
    await register(async_client, "taro@example.com")
    response = await login(async_client, email, password)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


async def test_user_without_password_cannot_login(async_client, db):
    # GraphQL の createUser で作ったユーザはパスワードを持たない
    db.add(User(name="no pw", email="nopw@example.com"))  # hashed_password は空
    await db.commit()
    response = await login(async_client, "nopw@example.com", "anything-at-all")
    assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


async def test_bcrypt_hash_is_upgraded_on_login(async_client, db):
    # passlib 時代の bcrypt のハッシュでもログインでき、そのとき Argon2 に置き換わる
    bcrypt_hash = BcryptHasher().hash(PASSWORD)
    user = User(name="old", email="old@example.com", hashed_password=bcrypt_hash)
    db.add(user)
    await db.commit()

    assert (
        await login(async_client, "old@example.com")
    ).status_code == status.HTTP_200_OK
    await db.refresh(user)
    assert user.hashed_password.startswith("$argon2id$")


@pytest.mark.parametrize("token", [None, "not-a-token"], ids=["トークン無し", "不正"])
async def test_me_requires_token(async_client, token):
    response = await Api(async_client, token).request("GET", "/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_revokes_token(async_client, db):
    api, _ = await signed_in(async_client, "taro@example.com")
    other_device = Api(
        async_client,
        (await login(async_client, "taro@example.com")).json()["access_token"],
    )

    assert (
        await api.request("POST", "/auth/logout")
    ).status_code == status.HTTP_204_NO_CONTENT
    assert (
        await api.request("GET", "/users/me")
    ).status_code == status.HTTP_401_UNAUTHORIZED
    # ログアウトしたのはその端末だけ
    assert (
        await other_device.request("GET", "/users/me")
    ).status_code == status.HTTP_200_OK


async def test_inactive_user_is_rejected(async_client, db):
    api, user = await signed_in(async_client, "taro@example.com")
    await db.execute(update(User).where(User.id == user["id"]).values(is_active=False))
    await db.commit()
    assert (
        await api.request("GET", "/users/me")
    ).status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        await login(async_client, "taro@example.com")
    ).status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------- 自分の情報の更新


async def test_update_me(async_client):
    api, user = await signed_in(async_client, "taro@example.com")
    response = await api.request(
        "PATCH",
        "/users/me",
        json={"name": "改名 太郎", "email": "new@example.com", "is_superuser": True},
    )
    assert response.status_code == status.HTTP_200_OK
    # 自分では管理者になれない。メールアドレスを変えると未確認に戻る
    assert response.json() == user | {
        "name": "改名 太郎",
        "email": "new@example.com",
        "is_verified": False,
    }


async def test_update_me_email_taken(async_client):
    await register(async_client, "taken@example.com")
    api, _ = await signed_in(async_client, "taro@example.com")
    response = await api.request(
        "PATCH", "/users/me", json={"email": "taken@example.com"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "UPDATE_USER_EMAIL_ALREADY_EXISTS"


@pytest.mark.parametrize(
    ("current", "new", "detail"),
    [
        ("wrong-password", "brand-new-password", "今のパスワードが違います"),
        (PASSWORD, PASSWORD, "新しいパスワードが今と同じです"),
        (PASSWORD, "short", "パスワードは 8 文字以上にしてください"),
    ],
    ids=["今のパスワード違い", "同じ", "短い"],
)
async def test_update_password_rejected(async_client, current, new, detail):
    api, _ = await signed_in(async_client, "taro@example.com")
    response = await api.request(
        "PATCH",
        "/users/me/password",
        json={"current_password": current, "new_password": new},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == detail


async def test_update_password_revokes_all_tokens(async_client, db):
    api, user = await signed_in(async_client, "taro@example.com")
    await login(async_client, "taro@example.com")  # 別の端末

    response = await api.request(
        "PATCH",
        "/users/me/password",
        json={"current_password": PASSWORD, "new_password": "brand-new-password"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    tokens = (
        await db.execute(select(AccessToken).where(AccessToken.user_id == user["id"]))
    ).all()
    assert tokens == []
    assert (
        await login(async_client, "taro@example.com")
    ).status_code == status.HTTP_400_BAD_REQUEST
    assert (
        await login(async_client, "taro@example.com", "brand-new-password")
    ).status_code == 200


async def test_delete_me_is_soft_delete(async_client, db):
    api, user = await signed_in(async_client, "taro@example.com")
    assert (
        await api.request("DELETE", "/users/me")
    ).status_code == status.HTTP_204_NO_CONTENT

    assert (
        await api.request("GET", "/users/me")
    ).status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        await login(async_client, "taro@example.com")
    ).status_code == status.HTTP_400_BAD_REQUEST
    row = await db.get(User, user["id"])
    assert row is not None and row.soft_destroyed_at is not None
    # 同じメールアドレスで登録し直せる
    assert (
        await register(async_client, "taro@example.com")
    ).status_code == status.HTTP_201_CREATED


async def test_superuser_cannot_delete_self(async_client, db):
    api, user = await signed_in(async_client, "admin@example.com")
    await make_superuser(db, user["id"])
    assert (
        await api.request("DELETE", "/users/me")
    ).status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------- パスワード再設定・メール確認


async def test_forgot_and_reset_password(async_client, mocker):
    await register(async_client, "taro@example.com")
    sent = mocker.patch.object(emails, "send_reset_password")

    # 登録の有無を漏らさないよう、居ないメールアドレスでも同じ 202
    for email in ("taro@example.com", "nobody@example.com"):
        response = await async_client.post(
            "/auth/forgot-password", json={"email": email}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
    sent.assert_called_once()
    _user, token = sent.call_args.args

    response = await async_client.post(
        "/auth/reset-password", json={"token": token, "password": "reset-new-password"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        await login(async_client, "taro@example.com", "reset-new-password")
    ).status_code == 200

    # 同じトークンは 2 回使えない（パスワードのハッシュが変わると無効になる）
    response = await async_client.post(
        "/auth/reset-password", json={"token": token, "password": "another-password"}
    )
    assert response.json()["detail"] == "RESET_PASSWORD_BAD_TOKEN"


async def test_verify_email(async_client, mocker):
    api, _ = await signed_in(async_client, "taro@example.com")
    sent = mocker.patch.object(emails, "send_verify")

    response = await async_client.post(
        "/auth/request-verify-token", json={"email": "taro@example.com"}
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    _user, token = sent.call_args.args

    response = await async_client.post("/auth/verify", json={"token": token})
    assert response.status_code == status.HTTP_200_OK
    assert (await api.request("GET", "/users/me")).json()["is_verified"] is True


# ---------------------------------------------------------------- 管理者


async def test_superuser_manages_users(async_client, db):
    admin, admin_user = await signed_in(async_client, "admin@example.com")
    await make_superuser(db, admin_user["id"])
    member, member_user = await signed_in(async_client, "member@example.com")
    url = f"/users/{member_user['id']}"

    # 一般ユーザは管理者の API を使えない
    for method, path in [
        ("GET", "/users"),
        ("GET", url),
        ("PATCH", url),
        ("DELETE", url),
    ]:
        response = await member.request(method, path, json={})
        assert response.status_code == status.HTTP_403_FORBIDDEN, (method, path)

    page = (await admin.request("GET", "/users", params={"limit": 1})).json()
    assert page["count"] == 2
    assert len(page["data"]) == 1

    assert (await admin.request("GET", url)).json() == member_user

    response = await admin.request(
        "PATCH", url, json={"is_superuser": True, "name": "昇格"}
    )
    assert response.json() == member_user | {"is_superuser": True, "name": "昇格"}

    assert (
        await admin.request("DELETE", url)
    ).status_code == status.HTTP_204_NO_CONTENT
    assert (await admin.request("GET", url)).status_code == status.HTTP_404_NOT_FOUND
    assert (
        await member.request("GET", "/users/me")
    ).status_code == status.HTTP_401_UNAUTHORIZED
    assert (await admin.request("GET", "/users")).json()["count"] == 1


# ---------------------------------------------------------------- 投稿（自分のものだけ触れる）


async def test_posts_ownership(async_client, db):
    alice, alice_user = await signed_in(async_client, "alice@example.com")
    bob, _ = await signed_in(async_client, "bob@example.com")

    response = await alice.request("POST", "/posts", json={"title": "alice の投稿"})
    assert response.status_code == status.HTTP_201_CREATED
    post = response.json()
    assert post["user_id"] == alice_user["id"]
    url = f"/posts/{post['id']}"

    assert (await alice.request("GET", "/posts")).json() == [post]
    assert (await bob.request("GET", "/posts")).json() == []
    for method, kwargs in [
        ("GET", {}),
        ("PATCH", {"json": {"title": "x"}}),
        ("DELETE", {}),
    ]:
        response = await bob.request(method, url, **kwargs)
        assert response.status_code == status.HTTP_403_FORBIDDEN, method

    response = await alice.request("PATCH", url, json={"title": "書き換え"})
    assert response.json() == post | {"title": "書き換え"}
    assert (
        await alice.request("DELETE", url)
    ).status_code == status.HTTP_204_NO_CONTENT
    assert (await alice.request("GET", url)).status_code == status.HTTP_404_NOT_FOUND
    assert (await Api(async_client).request("GET", "/posts")).status_code == 401


async def test_superuser_sees_all_posts(async_client, db):
    alice, _ = await signed_in(async_client, "alice@example.com")
    admin, admin_user = await signed_in(async_client, "admin@example.com")
    await make_superuser(db, admin_user["id"])
    post = (
        await alice.request("POST", "/posts", json={"title": "alice の投稿"})
    ).json()

    assert post in (await admin.request("GET", "/posts")).json()
    response = await admin.request(
        "PATCH", f"/posts/{post['id']}", json={"title": "管理者が直した"}
    )
    assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------- GraphQL


async def test_graphql_me_and_create_post(async_client):
    api, user = await signed_in(async_client, "taro@example.com")

    body = await api.graphql("{ me { id email } }")
    assert body == {"data": {"me": {"id": user["id"], "email": "taro@example.com"}}}

    body = await api.graphql(
        "mutation ($title: String!) { createPost(title: $title) { title userId } }",
        title="はじめての投稿",
    )
    assert body == {
        "data": {"createPost": {"title": "はじめての投稿", "userId": user["id"]}}
    }


async def test_graphql_after_logout(async_client):
    api, _ = await signed_in(async_client, "taro@example.com")
    await api.request("POST", "/auth/logout")
    body = await api.graphql("{ me { id } }")
    assert body["errors"][0]["message"] == "User is not authenticated"


@pytest.mark.parametrize("token", [None, "not-a-token"], ids=["トークン無し", "不正"])
async def test_graphql_me_requires_auth(async_client, token):
    api = Api(async_client, token)
    body = await api.graphql("{ me { id } }")
    assert body["data"] is None
    assert body["errors"][0]["message"] == "User is not authenticated"

    # ログイン不要のフィールドはトークンが無くても使える
    assert await api.graphql('{ hello(name: "graphql") }') == {
        "data": {"hello": "Hello, graphql!"}
    }
