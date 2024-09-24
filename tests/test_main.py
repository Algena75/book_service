import json

import pytest
from fastapi import status
from httpx import AsyncClient

from web.core.models import Book

NEW_BOOK = dict(name="Any new book",
                author="Any Author")


@pytest.mark.parametrize("endpoint", [("get", "/books"),
                                      ("get", "/books/1"),
                                      ("put", "/books/1"),
                                      ("delete", "/books/1"),
                                      ("post", "/books")])
@pytest.mark.anyio
async def test_unauthorized_user_cant_crud(client: AsyncClient, endpoint):
    """
    Неавторизованный пользователь не имеет доступа к функциям CRUD.
    """
    response = await getattr(client, endpoint[0])(endpoint[1])
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.parametrize("endpoint", [("get", "/books"), ("get", "/books/1")])
@pytest.mark.anyio
async def test_authorized_user_can_view_books(
    authenticated_client: AsyncClient, test_book: Book, endpoint
):
    """
    Авторизованный пользователь может просматривать записи.
    """
    response = await getattr(authenticated_client, endpoint[0])(endpoint[1])
    assert response.status_code == status.HTTP_200_OK
    assert test_book.name in response.text


@pytest.mark.anyio
async def test_authorized_user_can_add_book(authenticated_client: AsyncClient,
                                            test_book: Book):
    """
    Авторизованный пользователь может добавить запись.
    """
    response = await authenticated_client.post("/books",
                                               data=json.dumps(NEW_BOOK))
    assert response.status_code == status.HTTP_201_CREATED
    assert NEW_BOOK.get("name") in response.text


@pytest.mark.anyio
async def test_authorized_user_can_update_book(
    authenticated_client: AsyncClient, test_book: Book
):
    """
    Авторизованный пользователь может изменить запись.
    """
    response = await authenticated_client.get("/books/1")
    assert NEW_BOOK.get("name") not in response.text

    response = await authenticated_client.put("/books/1",
                                              data=json.dumps(NEW_BOOK))
    assert response.status_code == status.HTTP_200_OK
    assert NEW_BOOK.get("name") in response.text


@pytest.mark.anyio
async def test_authorized_user_can_delete_book(
    authenticated_client: AsyncClient, test_book: Book
):
    """
    Авторизованный пользователь может удалить запись.
    """
    response_1 = await authenticated_client.get("/books")
    await authenticated_client.delete("/books/1")
    response_2 = await authenticated_client.get("/books")
    assert len(response_1.json()) == len(response_2.json()) + 1

