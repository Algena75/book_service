from redis import Redis, RedisError

from web.core.config import settings as st


async def get_redis_client():
    try:
        return Redis(host=st.REDIS_HOST, port=st.REDIS_PORT)
    except:
        raise RedisError("Кеширование недоступно")
