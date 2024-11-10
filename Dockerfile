ARG PROD_TAG=latest
ARG RUNTIME_TAG=latest

# ベースイメージ
#FROM python:3.12 AS base
#軽量版に切り替える場合はこちらを使用
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 1. 開発用ランタイムのビルド
FROM base AS dev

COPY src /app/src
COPY README.md pyproject.toml .python-version uv.lock ./
COPY tests /app/tests
COPY alembic /app/alembic
COPY alembic.ini .env ./
RUN uv sync --frozen --no-cache --dev

## ローカルはあんまりここを分けるメリットがない
## 2. 開発用ランタイムを使用して起動
FROM dev_runtime AS dev

COPY src /app/src

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]

## 3. test 用
FROM kirimaru/fastapi-practice_dev-runtime:${RUNTIME_TAG} AS test
ARG RUNTIME_TAG

# NOTE: compose ファイルでマウントするなら不要
COPY src /app/src

# 4. 本番用ランタイムのビルド
FROM base AS prod_runtime

COPY README.md pyproject.toml .python-version uv.lock ./

RUN uv sync --frozen --no-cache

# 5. 本番用ランタイムを使用して起動
#FROM kirimaru/fastapi-practice_prod-runtime:${PROD_TAG} AS prod
# TODO: まずは固定で動くことの確認
#FROM kirimaru/fastapi-practice_prod-runtime:latest AS prod
FROM kirimaru/fastapi-practice_prod-runtime:0.0.1 AS prod
COPY src /app/src
COPY .env ./

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
