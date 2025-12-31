# -*- coding: utf-8 -*-

from fastapi import APIRouter

from src.api.routers import (array_factory, dependency_injection, done,
                             exception, generate_api, healthcheck,
                             notification, pydantic, questions, task, user)

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
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
