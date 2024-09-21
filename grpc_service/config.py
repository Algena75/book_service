import os
from asyncpg.pool import Pool

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
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

    class Config:
        env_file = '.env'
        extra = 'allow'


settings = Settings()
