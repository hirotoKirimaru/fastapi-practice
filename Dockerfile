ARG RUNTIME_TAG=latest
ARG UV_VERSION=0.8.17
ARG PYTHON_VERSION=3.14-slim

# ベースイメージ
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# uv をバージョン固定で取得
COPY --from=ghcr.io/astral-sh/uv:${UV_VERSION} /uv /usr/local/bin/uv

# 1. 開発用ランタイムのビルド
FROM base AS dev_runtime

# 依存関係のみ先にインストール（lock変更がない限りキャッシュ）
COPY pyproject.toml uv.lock .python-version README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-groups

# プロジェクト本体をコピー
COPY src /app/src
COPY tests /app/tests
COPY alembic /app/alembic
COPY alembic.ini pytest.ini ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups

## 2. 開発用ランタイムを使用して起動
FROM dev_runtime AS dev

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]

## 3. test 用
ARG RUNTIME_TAG
FROM kirimaru/fastapi-practice_dev-runtime:${RUNTIME_TAG} AS test

# CI 用に起動しっぱなしであってほしい
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]


# 4. 本番用ランタイムのビルド
FROM base AS prod_runtime

COPY pyproject.toml uv.lock .python-version README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY src /app/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 5. 本番用ランタイムを使用して起動（最終イメージは distroless 風に最小化）
ARG RUNTIME_TAG
FROM kirimaru/fastapi-practice_prod-runtime:${RUNTIME_TAG} AS prod

# 非 root ユーザで実行
RUN groupadd --system app && useradd --system --gid app --home /app app \
    && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/docs', timeout=3).status==200 else 1)" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
