import json

import pytest
from fastapi import status
from httpx import AsyncClient

NEW_USER = dict(email="user@example.com",
                password="string")


@pytest.mark.anyio
class TestAuth:

    async def test_any_user_can_register(self, client: AsyncClient,
                                         authenticated_client: AsyncClient):
        """
        Любой пользователь может зарегистрироваться.
        """
        response = await client.post("/auth/register",
                                     data=json.dumps(NEW_USER))
        assert response.status_code == status.HTTP_201_CREATED
        assert NEW_USER.get("email") in response.text


    async def test_new_user_can_get_token(self, client: AsyncClient):
        """
        Пользователь при аутентификации получает действительный токен.
        """
        new_user_token = await client.post(
            "/auth/jwt/login",
            data={'username': "user@example.com", 'password': "string"}
        )
        assert new_user_token.status_code == status.HTTP_200_OK
        assert "access_token" in new_user_token.json()
        NEW_USER['access_token'] = (
            f'Bearer {new_user_token.json().get("access_token")}'
        )

    @pytest.mark.parametrize("endpoint", [("get", "/books"),
                                          ("get", "/books/2")])
    async def test_new_user_can_get_crud(self, client: AsyncClient, endpoint):
        """
        Пользователь по токену получает доступ к CRUD.
        """
        response = await getattr(
            client, endpoint[0]
        )(endpoint[1], headers={'Authorization': NEW_USER["access_token"]})
        assert response.status_code == status.HTTP_200_OK
