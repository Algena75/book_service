from http import HTTPStatus
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from web.api.endpoints.validators import validate_new_book
from web.core.crud import book_crud
from web.core.db import get_async_session
from web.core.rabbitmq import send_message_to_broker
from web.core.user import current_user
from web.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(tags=['books'], dependencies=[Depends(current_user)])


@router.get('/books', response_model=List[BookRead])
async def get_books_list(
    session: AsyncSession = Depends(get_async_session),
) -> List[BookRead]:
    """Возвращает список книг."""
    all_books = await book_crud.get_multi(session)
    if len(all_books) == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Список книг пуст!'
        )
    return all_books


@router.post('/books', response_model=BookRead,
             status_code=HTTPStatus.CREATED)
async def create_new_book(
    new_book: BookCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """Создаёт новую запись о книге."""
    new_book = new_book.model_dump()
    await validate_new_book(new_book, session)
    book = await book_crud.create(BookCreate(**new_book), session)
    await send_message_to_broker(f'Добавлена книга {str(book.dict())}')
    return book


@router.get('/books/{id}', response_model=BookRead)
async def get_book(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> BookRead:
    """Возвращает список книг."""
    book = await book_crud.get(id, session)
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Книга не найдена!'
        )
    return book


@router.put('/books/{id}', response_model=BookRead)
async def update_book(
    id: int,
    data_to_update: BookUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """Обновляет ранее созданную запись о книге."""
    data_to_update = data_to_update.model_dump()
    data_set = set(data_to_update.values())
    if len(data_set) == 1 and None in data_set:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нет данных для изменения!'
        )
    book_to_update = await book_crud.get(id, session)
    if not book_to_update:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Книга для изменения не найдена!'
        )
    data = BookCreate(**(book_to_update.dict())).model_dump()
    for key in data.keys():
        if not data_to_update.get(key):
            data_to_update[key] = data.get[key]
    await validate_new_book(data_to_update, session)
    book = await book_crud.update(book_to_update,
                                  BookUpdate(**data_to_update), session)
    await send_message_to_broker(f'Обновлена книга {str(book.dict())}')
    return book


@router.delete('/books/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_mem(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет ранее созданную запись о книге."""
    book_to_delete = await book_crud.get(obj_in=id, session=session)
    if book_to_delete:
        await book_crud.remove(db_obj=book_to_delete, session=session)
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Запись о книге не найдена!'
        )
    await send_message_to_broker(f'Удалена книга id: {id}')
