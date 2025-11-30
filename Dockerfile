# Multi-stage build for Python Flask app using uv
# Based on:
# - https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# - https://cloud.google.com/run/docs/tips/python

# Stage 1: Builder - Install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Use copy link mode for cache mounts on different filesystems
ENV UV_LINK_MODE=copy

# Disable Python downloads - use system interpreter across both images
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy application source code
COPY . /app

# Install the project with already installed dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim-bookworm

# Create non-root user for security (matching official example pattern)
RUN groupadd --system --gid 999 appuser \
    && useradd --system --gid 999 --uid 999 --create-home appuser

# Copy application from builder
COPY --from=builder --chown=appuser:appuser /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set Python to run in unbuffered mode (better for container logs)
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Use /app as the working directory
WORKDIR /app

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run gunicorn with Google Cloud Run recommended settings:
# - bind to $PORT environment variable (Cloud Run sets this, default to 8080)
# - workers=1 (Cloud Run handles horizontal scaling)
# - threads=8 (handle concurrent requests efficiently)
# - timeout=0 (Cloud Run manages request timeouts)
# - preload app for better error detection and memory efficiency
CMD exec gunicorn --bind :${PORT:-8080} \
     --workers 1 \
     --threads 8 \
     --timeout 0 \
     --preload \
     --access-logfile - \
     --error-logfile - \
     "app:create_app()"
