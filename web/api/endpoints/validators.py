from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web.core.models import Book


async def validate_new_book(new_book: dict, session: AsyncSession) -> None:
    """Создаёт новую запись о книге."""
    book = await session.execute(select(Book).where(
        Book.name == new_book.get("name"),
        Book.author == new_book.get("author")
    ))
    if book.scalars().first():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Такая книга существует!'
        )
