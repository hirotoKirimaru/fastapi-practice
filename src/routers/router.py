# -*- coding: utf-8 -*-

from fastapi import APIRouter
from src.routers import done, exception, healthcheck, task, notification

api_router = APIRouter()

api_router.include_router(task.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(done.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(notification.router, prefix="/notification", tags=["notifications"])
api_router.include_router(healthcheck.router, prefix="/health")
api_router.include_router(exception.router, prefix="/exception")
