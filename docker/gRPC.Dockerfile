FROM python:3.10-slim

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./README.md /app/

COPY ./grpc_service /app/grpc_service
COPY ./protobufs /app/protobufs

RUN apt update && pip install poetry==1.7.0 \
    && poetry config virtualenvs.create false \
    && poetry install --without test,web --no-interaction --no-ansi

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT [ "python", "/app/grpc_service/main.py" ]
