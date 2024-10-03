import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from web.core.models import Book

NEW_BOOK = dict(name="Any new book",
                author="Any Author")
NEW_USER = dict(email="user@example.com",
                password="string")


@pytest.mark.anyio
class TestAPI:

    @pytest.mark.parametrize("endpoint", [("get", "/books"),
                                          ("get", "/books/1"),
                                          ("put", "/books/1"),
                                          ("delete", "/books/1"),
                                          ("post", "/books")])
    async def test_unauthorized_user_cant_crud(self, client: AsyncClient,
                                               endpoint):
        """
        Неавторизованный пользователь не имеет доступа к функциям CRUD.
        """
        response = await getattr(client, endpoint[0])(endpoint[1])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Unauthorized"}


    @pytest.mark.parametrize("endpoint", [("get", "/books"),
                                          ("get", "/books/1")])
    async def test_authorized_user_can_view_books(
        self, authenticated_client: AsyncClient, test_book: Book, endpoint,
    ):
        """
        Авторизованный пользователь может просматривать записи.
        """
        response = await getattr(authenticated_client,
                                 endpoint[0])(endpoint[1])
        assert response.status_code == status.HTTP_200_OK
        assert test_book.name in response.text


    async def test_authorized_user_can_add_book(
        self, authenticated_client: AsyncClient
    ):
        """
        Авторизованный пользователь может добавить запись.
        """
        response = await authenticated_client.post("/books",
                                                   data=json.dumps(NEW_BOOK))
        assert response.status_code == status.HTTP_201_CREATED
        assert NEW_BOOK.get("name") in response.text


    async def test_authorized_user_cant_add_the_same_book(
        self, authenticated_client: AsyncClient
    ):
        """
        Авторизованный пользователь не может добавить дублирующуюся запись.
        """
        response = await authenticated_client.post("/books",
                                                   data=json.dumps(NEW_BOOK))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Такая книга существует!' in response.text


    async def test_authorized_user_cant_update_book_with_duplicate_data(
        self, authenticated_client: AsyncClient, 
    ):
        """
        Авторизованный пользователь не может изменить запись с дублирующимися
        данными.
        """
        response = await authenticated_client.put("/books/1",
                                                  data=json.dumps(NEW_BOOK))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Такая книга существует!' in response.text


    async def test_authorized_user_can_update_book(
        self, authenticated_client: AsyncClient, 
    ):
        """
        Авторизованный пользователь может изменить запись.
        """
        NEW_BOOK["name"] = "different name"
        response = await authenticated_client.get("/books")
        assert NEW_BOOK.get("name") not in response.text

        response = await authenticated_client.put("/books/1",
                                                  data=json.dumps(NEW_BOOK))
        assert response.status_code == status.HTTP_200_OK
        assert NEW_BOOK.get("name") in response.text


    async def test_authorized_user_can_delete_book(
        self, authenticated_client: AsyncClient, async_db: AsyncSession
    ):
        """
        Авторизованный пользователь может удалить запись.
        """
        response_1 = await async_db.execute(func.count(Book.id))
        response_1 = response_1.scalar()
        await authenticated_client.delete("/books/2")
        response_2 = await async_db.execute(func.count(Book.id))
        response_2 = response_2.scalar()
        assert response_1 == response_2 + 1


    async def test_safe_methods_use_cache(
        self, authenticated_client: AsyncClient, redis_client,
    ):
        """
        Безопасные методы используют кеш.
        """
        redis_client.delete('get_books_list')
        redis_client.delete('get_book-id=1')
        response_1 = await authenticated_client.get("/books")
        response_2 = await authenticated_client.get("/books/1")
        assert NEW_BOOK.get("name") in response_1.text
        assert NEW_BOOK.get("name") in response_2.text

        NEW_BOOK['name'] = 'Cool name for cool book'
        await authenticated_client.put("/books/1",
                                       data=json.dumps(NEW_BOOK))
        response_1 = await authenticated_client.get("/books")
        response_2 = await authenticated_client.get("/books/1")
        assert NEW_BOOK.get("name") not in response_1.text
        assert NEW_BOOK.get("name") not in response_2.text

        redis_client.delete('get_books_list')
        redis_client.delete('get_book-id=1')

        response_1 = await authenticated_client.get("/books")
        response_2 = await authenticated_client.get("/books/1")
        assert NEW_BOOK.get("name") in response_1.text
        assert NEW_BOOK.get("name") in response_2.text
