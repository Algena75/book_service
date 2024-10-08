import os
from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = 'Сервис для управления списком книг'
    APP_DESCRIPTION: str = 'Тестовое задание'

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str | int = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    DATABASE_URL: str = (f"postgresql+asyncpg://{POSTGRES_USER}:"
                         f"{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:"
                         f"{POSTGRES_PORT}/{POSTGRES_DB}")
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    RABBITMQ_USER: str = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_QUEUE: str = os.getenv('RABBITMQ_QUEUE', 'hello')
    REDIS_HOST: str = os.getenv('REDIS_HOST', "localhost")
    REDIS_PORT: str | int = os.getenv('REDIS_PORT', 6379)
    LOCAL_REDIS_URL: str = (f"redis://{REDIS_HOST}:{REDIS_PORT}")
    CACHE_EXPIRE: int = 60

    class Config:
        env_file = '.env'
        extra = 'allow'


settings = Settings()

LIFETIME = 3600
