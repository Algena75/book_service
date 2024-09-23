FROM python:3.10-slim

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./README.md ./alembic.ini /app/

COPY ./web /app/web
COPY ./alembic /app/alembic
COPY ./docker /app

RUN apt update && pip install poetry==1.7.0 \
    && poetry config virtualenvs.create false \
    && poetry install --without test,grpc_service --no-interaction --no-ansi

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN chmod +x /app/server-entrypoint.sh
