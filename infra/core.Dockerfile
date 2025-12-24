FROM python:3.12 AS base

RUN mkdir /app
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml /app
COPY uv.lock /app
COPY migrations /app/migrations
COPY src /app/src

RUN uv sync --no-dev --locked

CMD uv run pw_migrate migrate --database mysql://$MARIADB_USER:$MARIADB_PASSWORD@$MARIADB_HOST:$MARIADB_PORT/$MARIADB_DATABASE \
    && uv run gunicorn --bind 0.0.0.0:5000 src.api:app