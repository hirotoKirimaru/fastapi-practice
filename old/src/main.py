from fastapi import FastAPI

from src.routers.router import api_router


app = FastAPI()
# app.include_router(api_router, prefix="/v1")
app.include_router(api_router)
