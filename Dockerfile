FROM python:3.12 AS base
#FROM python:3.12-slim AS base # 後でこっちに戻す

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
#ENV PYTHONPATH="/app:$PYTHONPATH"
#ENV PATH="/app/.venv/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /app

COPY src /app/src
COPY README.md pyproject.toml .python-version uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock ./

FROM base AS development

COPY tests /app/tests
COPY alembic /app/alembic
COPY alembic.ini .env ./
RUN uv sync --frozen --no-cache --dev
#RUN uv pip install --no-cache -e .[dev] --system
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0"]

FROM base AS production

#RUN uv pip install --no-cache -e . --system
RUN uv sync --frozen --no-cache
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0"]