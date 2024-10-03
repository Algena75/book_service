import fakeredis
import pytest


@pytest.fixture(scope='session')
async def redis_client():
    return fakeredis.FakeRedis()
