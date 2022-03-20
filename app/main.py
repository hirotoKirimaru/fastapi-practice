# -*- coding: utf-8 -*-

from api.routers import endpoint, healthcheck
from fastapi import FastAPI

app = FastAPI()

app.include_router(endpoint.router)
app.include_router(healthcheck.router, prefix="/health")