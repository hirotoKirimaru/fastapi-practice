# -*- coding: utf-8 -*-

from fastapi import APIRouter
from src.api.routers import (
    done,
    exception,
    healthcheck,
    notification,
    task,
    generate_api,
    dependency_injection,
    array_factory,
    user
)

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