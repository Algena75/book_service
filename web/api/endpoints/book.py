import json
from http import HTTPStatus
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from web.api.endpoints.validators import validate_book_exist, validate_new_book
from web.core.config import settings
from web.core.crud import book_crud
from web.core.db import get_async_session
from web.core.rabbitmq import send_message_to_broker
from web.core.redis import get_redis_client
from web.core.user import current_user
from web.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(tags=['books'], dependencies=[Depends(current_user)])


@router.get('/books', response_model=List[BookRead])
async def get_books_list(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis_client)
) -> List[BookRead]:
    """Возвращает список книг."""
    redis_key = get_books_list.__name__
    cached_data = redis.get(redis_key)
    if cached_data:
        all_books = json.loads(cached_data)
    else:
        all_books = await book_crud.get_multi(session)
        if len(all_books) == 0:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Список книг пуст!'
            )
        redis.set(name=redis_key, value=json.dumps(all_books),
                  ex=settings.CACHE_EXPIRE)
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
    redis: Redis = Depends(get_redis_client)
) -> BookRead:
    """Возвращает книгy по id."""
    redis_key = f'{get_book.__name__}-id={id}'
    cached_data = redis.get(redis_key)
    if cached_data:
        book = json.loads(cached_data)
    else:
        book = await validate_book_exist(id, session)
        redis.set(name=redis_key, value=json.dumps(book.dict()),
                  ex=settings.CACHE_EXPIRE)
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
    book_to_update = await validate_book_exist(id, session)
    data = BookCreate(**(book_to_update.dict())).model_dump()
    for key in data.keys():
        if not data_to_update.get(key):
            data_to_update[key] = data.get(key)
    await validate_new_book(data_to_update, session)
    book = await book_crud.update(book_to_update,
                                  BookUpdate(**data_to_update), session)
    await send_message_to_broker(f'Обновлена книга {str(book.dict())}')
    return book


@router.delete('/books/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_book(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет ранее созданную запись о книге."""
    book_to_delete = await validate_book_exist(id, session)
    await book_crud.remove(db_obj=book_to_delete, session=session)
    await send_message_to_broker(f'Удалена книга id: {id}')
