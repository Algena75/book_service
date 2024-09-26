from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web.core.models import Book
from web.core.crud import book_crud


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


async def validate_book_exist(book_id: int,
                              session: AsyncSession) -> Book | dict:
    """Возвращает книгу, если она существует."""
    book = await book_crud.get(book_id, session)
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Книга c id={book_id} не найдена!'
        )
    return book
