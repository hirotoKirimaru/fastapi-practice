ARG RUNTIME_TAG=latest

# ベースイメージ
#FROM python:3.12 AS base
#軽量版に切り替える場合はこちらを使用
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
#ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 1. 開発用ランタイムのビルド
FROM base AS dev_runtime

COPY src /app/src
COPY README.md pytest.ini pyproject.toml .python-version uv.lock ./
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
ARG RUNTIME_TAG
FROM kirimaru/fastapi-practice_dev-runtime:${RUNTIME_TAG} AS test

# NOTE: compose ファイルでマウントするなら不要
COPY src /app/src

# CI用に起動しっぱなしであってほしい
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]


# 4. 本番用ランタイムのビルド
FROM base AS prod_runtime

COPY README.md pyproject.toml .python-version uv.lock ./

RUN uv sync --frozen --no-cache

# 5. 本番用ランタイムを使用して起動
ARG RUNTIME_TAG
FROM kirimaru/fastapi-practice_prod-runtime:${RUNTIME_TAG} AS prod

COPY src /app/src
COPY .env ./

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
