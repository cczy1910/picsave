import aioredis

from datetime import timedelta

from common.exit_util import safe_exit

redis_client = None


async def get_client(cfg: dict[str]) -> aioredis.client.Redis:
    global redis_client
    if redis_client is None:
        redis_client = await redis_connect(cfg)

    return redis_client


async def redis_connect(cfg: dict[str]) -> aioredis.client.Redis:
    try:
        client = aioredis.Redis(**cfg)

        ping = await client.ping()
        if ping is True:
            return client
    except aioredis.AuthenticationError as e:
        safe_exit(f'Unable to connect to Redis: {str(e)}')


async def get_from_cache(client: aioredis.client.Redis, key: str) -> bytes:
    val = await client.get(key)
    return val


async def set_to_cache(client: aioredis.client.Redis, key: str, value: bytes) -> bool:
    state = await client.set(key, value=value, ex=timedelta(hours=1))
    return state
