FROM docker.io/library/python:3.12-slim-bookworm AS base

ENV PATH="/venv/bin:${PATH}" \
    UV_PROJECT_ENVIRONMENT="/venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

FROM base AS build

RUN apt update && \
    apt-get install -y --no-install-recommends gcc git && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /usr/local/bin/

COPY ./pyproject.toml /pyproject.toml

RUN uv sync --no-default-groups --no-install-project --link-mode=copy

FROM base

COPY --from=build /venv /venv

COPY ./alembic.ini ./alembic.ini
COPY ./maxhack ./maxhack
COPY ./migrations ./migrations
