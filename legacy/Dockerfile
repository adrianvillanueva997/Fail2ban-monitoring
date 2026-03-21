FROM python:3.13-slim-bookworm AS base

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.main"]

FROM base AS sqlite
RUN uv sync --extra "sqlite"
ENV DB_TYPE=sqlite
ENV DB_NAME=/app/data/fail2ban.db
RUN mkdir -p /app/data

FROM base AS postgres
RUN uv sync --extra "postgres"
ENV DB_TYPE=postgres

FROM base AS mariadb
RUN uv sync --extra "mysql"
ENV DB_TYPE=mariadb