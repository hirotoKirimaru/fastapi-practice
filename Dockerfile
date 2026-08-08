# syntax=docker/dockerfile:1.7
ARG RUNTIME_TAG=latest

# ベースイメージ
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# イメージ内の venv はビルド時に確定済みなので、`uv run` が起動のたびに再 sync
# するのを止める。コンテナ起動が速くなり、実行時に venv へ書き込まなくなる。
# (これが無いと `uv run` が pyproject.toml の default-groups を見て、下でわざわざ
#  除外した analyze グループをテスト実行時に入れ直してしまう)
ENV UV_NO_SYNC=1

WORKDIR /app

# uv をバージョン固定で取得
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /usr/local/bin/uv

# 1. 開発用ランタイムのビルド
FROM base AS dev_runtime

# analyze グループ(jupyter/matplotlib 系 80 パッケージ)は src/tests から一切
# 使っていないので、このイメージには入れない。ローカルで notebook を触るときは
# ホスト側で `uv sync --group analyze` する
ARG UV_GROUPS="--no-default-groups --group api --group auth --group worker --group dev"

# 依存の解決だけを先に済ませてレイヤを分ける。
# src/tests を触っただけでは 200 パッケージの再インストールが走らなくなる
COPY README.md pyproject.toml .python-version uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project ${UV_GROUPS}

COPY src /app/src
COPY tests /app/tests
COPY alembic /app/alembic
COPY alembic.ini pytest.ini ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen ${UV_GROUPS}

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

# `--no-dev` は dev グループしか外さないため、default-groups に入っている
# analyze(jupyter/matplotlib) が本番イメージにまで載っていた。必要な
# グループだけを明示する
ARG UV_GROUPS="--no-default-groups --group api --group auth --group worker"

COPY README.md pyproject.toml .python-version uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project ${UV_GROUPS}

COPY src /app/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen ${UV_GROUPS}

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
