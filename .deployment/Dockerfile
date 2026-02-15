FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

FROM python:3.13-slim-bookworm AS runtime
ARG APP_RELEASE=not-set
ENV APP_RELEASE=$APP_RELEASE
RUN apt-get update && apt-get install -y curl && apt-get clean
WORKDIR /app
COPY --from=builder --chown=app:app  /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["poe", "start-prod"]
