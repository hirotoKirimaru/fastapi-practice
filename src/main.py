from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.api.main import api_router
from src.middleware.sentry import Sentry

Sentry.init_sentry()

app = FastAPI()
# app = FastAPI(default_response_class=ORJSONResponse)
# app.include_router(api_router, prefix="/v1")
app.include_router(api_router)

app.add_middleware(SentryAsgiMiddleware)

# TODO: 変な状態で定義していると動かない
# @app.middleware("http")
# async def add_request_id_middleware(
#     request: Request, call_next: Callable[[Request], Awaitable[Response]]
# ) -> Any:
#     pass
# TODO: ログまで出したい
# TODO: fom sentry_sdk import Hub
#
# with Hub.current.push_scope() as scope:
#    for key, value in scope._scope.items():
#        logger.info('%s: %s', key, value)

# request_id = str(uuid.uuid4())
# request.state.request_id = request_id
#
# response = await call_next(request)
# response.headers["X-Request-ID"] = request_id


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "SystemError"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": "BadRequestException"},
    )


import sqlalchemy  # noqa
