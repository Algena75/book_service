import os
from asyncpg.pool import Pool

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str | int = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    CONNECTION_DATA: dict = dict(host=POSTGRES_SERVER,
                                 port=POSTGRES_PORT,
                                 user=POSTGRES_USER,
                                 database=POSTGRES_DB,
                                 password=POSTGRES_PASSWORD)
    DB_POOL: Pool | None = None
    GRPS_SERVER: str = os.getenv("GRPS_SERVER", 'localhost')
    GRPC_PORT: str | int = os.getenv("GRPC_PORT", 50051)
    RABBITMQ_USER: str = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_QUEUE: str = os.getenv('RABBITMQ_QUEUE', 'hello')

    class Config:
        env_file = '.env'
        extra = 'allow'


settings = Settings()
