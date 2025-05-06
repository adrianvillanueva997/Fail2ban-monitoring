FROM python:3.13-slim-bookworm AS BASE

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
FROM BASE AS sqlite
RUN uv sync --extra "sqlite"
ENV DB_TYPE=sqlite
ENV DB_NAME=/app/data/fail2ban.db
RUN mkdir -p /app/data

# PostgreSQL variant
FROM BASE AS postgres
RUN uv sync --extra "postgres"
ENV DB_TYPE=postgres

# MariaDB variant
FROM BASE AS mariadb
RUN uv sync --extra "mysql"
ENV DB_TYPE=mariadb