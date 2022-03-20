# -*- coding: utf-8 -*-

from api.routers import endpoint, healthcheck
from fastapi import APIRouter

router = APIRouter()

router.include_router(endpoint.router)
router.include_router(healthcheck.router, prefix="/health")