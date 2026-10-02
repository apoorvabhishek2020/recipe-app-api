# ==============================================================================
# Stage 1: Base - Shared environment, uv binary, and dependency files
# ==============================================================================
FROM python:3.14-slim AS base
LABEL maintainer="apoorvabhishek.com"

# Python and uv environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT="/venv" \
    PATH="/venv/bin:$PATH"

# Install uv from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set container working directory
WORKDIR /app

# Create unprivileged system user
RUN adduser --disabled-password --gecos "" --no-create-home django-user

# Copy only dependency definitions first to maximize Docker layer caching
COPY pyproject.toml uv.lock .python-version ./

# ==============================================================================
# Stage 2: Development - Auto-reload server and all dependencies
# ==============================================================================
FROM base AS development

# Install all dependencies (including development groups)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy application source code and set ownership
COPY --chown=django-user:django-user ./app /app
RUN chown -R django-user:django-user /venv

USER django-user

EXPOSE 8000

# Django development server with auto-reload
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# Stage 3: Production - Hardened image with strictly production dependencies
# ==============================================================================
FROM base AS production

# Install strictly production dependencies (omits dev tools)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application source code and set ownership
COPY --chown=django-user:django-user ./app /app
RUN chown -R django-user:django-user /venv

USER django-user

EXPOSE 8000

# Production WSGI server (multi-worker, high concurrency)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app.wsgi:application"]
