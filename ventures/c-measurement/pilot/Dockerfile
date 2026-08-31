# Base image for the buildability pilot: one per Python minor version.
# Build:  docker build --build-arg PYVER=3.12 -t pilot-py:3.12 .
ARG PYVER=3.12
FROM python:${PYVER}-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /usr/local/bin/
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*
ENV UV_CACHE_DIR=/uvcache \
    PIP_CACHE_DIR=/pipcache \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
