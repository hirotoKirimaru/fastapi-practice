# syntax=docker/dockerfile:1.7
ARG RUNTIME_TAG=latest

# ベースイメージ
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# uv をバージョン固定で取得
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /usr/local/bin/uv

# 1. 開発用ランタイムのビルド
FROM base AS dev_runtime

COPY src /app/src
COPY README.md pytest.ini pyproject.toml .python-version uv.lock ./
COPY tests /app/tests
COPY alembic /app/alembic
COPY alembic.ini ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups

## 2. 開発用ランタイムを使用して起動
FROM dev_runtime AS dev

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]

## 3. test 用
ARG RUNTIME_TAG
FROM kirimaru/fastapi-practice_dev-runtime:${RUNTIME_TAG} AS test

COPY src /app/src
COPY tests /app/tests

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]


# 4. 本番用ランタイムのビルド
FROM base AS prod_runtime

COPY README.md pyproject.toml .python-version uv.lock ./
COPY src /app/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 5. 本番用ランタイム
ARG RUNTIME_TAG
FROM kirimaru/fastapi-practice_prod-runtime:${RUNTIME_TAG} AS prod

COPY src /app/src

# 非 root ユーザで実行
RUN groupadd --system app && useradd --system --gid app --home /app app \
    && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/docs', timeout=3).status==200 else 1)" || exit 1

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
