import pytest
from fastapi import status
from httpx import AsyncClient
import json

new_user = {
    "email": "user@example.com",
    "password": "string"
}


@pytest.mark.anyio
class TestAuthAPI:

    @classmethod
    def setUpClass(cls, client):
        cls.client = client

    async def test_client_can_register(self, client):
        response = await client.post("/auth/register", data=json.dumps(new_user))
        print(response.__dict__)
        assert new_user.get('email') not in response.json()
