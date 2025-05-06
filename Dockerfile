FROM python:3.13-slim-bookworm AS base

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Set common environment variables
ENV PYTHONUNBUFFERED=1

# Base command to run when container starts
CMD ["python", "-m", "src.main"]

# SQLite variant
FROM base AS sqlite
RUN uv sync --extra "sqlite"
ENV DB_TYPE=sqlite
ENV DB_NAME=/app/data/fail2ban.db
RUN mkdir -p /app/data

# PostgreSQL variant
FROM base AS postgres
RUN uv sync --extra "postgres"
ENV DB_TYPE=postgres

# MariaDB variant
FROM base AS mariadb
RUN uv sync --extra "mysql"
ENV DB_TYPE=mariadb