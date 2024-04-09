from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi import FastAPI
from src.middleware.sentry import Sentry
from src.routers.router import api_router

Sentry.init_sentry()

app = FastAPI()
# app.include_router(api_router, prefix="/v1")
app.include_router(api_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "SystemError"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "BadRequestException"},
    )
