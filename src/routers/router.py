# -*- coding: utf-8 -*-

from src.routers import task, done, healthcheck
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(task.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(done.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(healthcheck.router, prefix="/health")
