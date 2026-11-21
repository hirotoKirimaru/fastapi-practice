from fastapi import APIRouter

from src.api.routers import (
    array_factory,
    dependency_injection,
    done,
    exception,
    generate_api,
    healthcheck,
    job,
    notification,
    post,
    pydantic,
    questions,
    task,
    user,
)
from src.auth.backend import auth_backend, fastapi_users
from src.schemas.auth import UserCreate, UserRead, UserUpdate

api_router = APIRouter()

# 認証・ユーザ管理（fastapi-users）。
#   /auth/login, /auth/logout, /auth/register, /auth/forgot-password, /auth/reset-password,
#   /auth/request-verify-token, /auth/verify, /users/me, /users/{id}（管理者）
api_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)
api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
api_router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
api_router.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)
# fastapi-users に無いもの（一覧・退会・パスワード変更など）。/users/{id} より先に登録する
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
api_router.include_router(post.router, prefix="/posts", tags=["posts"])
api_router.include_router(task.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(done.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(
    notification.router, prefix="/notification", tags=["notifications"]
)
api_router.include_router(healthcheck.router, prefix="/health")
api_router.include_router(exception.router, prefix="/exception")
api_router.include_router(generate_api.router, prefix="/gen", tags=["generate"])
api_router.include_router(dependency_injection.router, prefix="/di", tags=["di"])
api_router.include_router(array_factory.router, prefix="/array", tags=["array"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(pydantic.router, prefix="/pydantic", tags=["pydantic"])
api_router.include_router(job.router, prefix="/jobs", tags=["jobs"])
