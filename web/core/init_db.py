import contextlib

import asyncpg
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from web.core.config import settings
from web.core.db import get_async_session
from web.core.models import User
from web.core.user import get_user_db, get_user_manager
from web.schemas.user import UserCreate

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
        email: EmailStr, password: str, is_superuser: bool = False
) -> User:
    """Создаёт и возвращет экземпляр пользователя."""
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user_created = await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser
                        )
                    )
                    return user_created
    except UserAlreadyExists:
        pass


async def create_first_superuser():
    """Создаёт первого суперпользователя при запуске проекта."""
    if (settings.first_superuser_email is not None and
            settings.first_superuser_password is not None):
        await create_user(
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            is_superuser=True,
        )


async def create_db_if_not_exists():
    """Создаём БД, если не существует."""
    try:
        connection = await asyncpg.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            database=settings.POSTGRES_DB,
            password=settings.POSTGRES_PASSWORD
        )
        print(f'Подключено! Необходимая БД {settings.POSTGRES_DB} обнаружена')
        await connection.close()
        return
    except:
        connection = await asyncpg.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user='postgres',
            database='template1',
            password='postgres'
        )
        CREATE_DB = f"""
        CREATE DATABASE {settings.POSTGRES_DB}
        OWNER '{settings.POSTGRES_USER}';
        """
        await connection.execute(CREATE_DB)
        print('База создана!')
        await connection.close()
        await create_db_if_not_exists()
