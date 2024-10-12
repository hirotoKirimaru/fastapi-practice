FROM python:3.12 AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/src:$PYTHONPATH"

WORKDIR /app

COPY src /app/src
COPY README.md pyproject.toml uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN uv sync --frozen --no-cache

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/src:$PYTHONPATH"

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /bin/uv /bin/uv

CMD ["uv", "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0"]