from redis.asyncio import Redis

from app.core.config import get_settings

redis_client: Redis | None = None


async def connect_redis() -> None:
    global redis_client
    settings = get_settings()
    redis_client = Redis.from_url(settings.redis_uri, decode_responses=True)


async def disconnect_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis is not connected")
    return redis_client
