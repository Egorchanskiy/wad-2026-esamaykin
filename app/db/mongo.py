from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

mongo_client: AsyncIOMotorClient | None = None


async def connect_mongo() -> None:
    global mongo_client
    settings = get_settings()
    mongo_client = AsyncIOMotorClient(settings.mongo_uri)


async def disconnect_mongo() -> None:
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()
        mongo_client = None


def get_db() -> AsyncIOMotorDatabase:
    if mongo_client is None:
        raise RuntimeError("MongoDB is not connected")
    settings = get_settings()
    return mongo_client[settings.mongo_db]
