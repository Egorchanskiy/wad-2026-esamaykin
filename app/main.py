from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.db.mongo import connect_mongo, disconnect_mongo
from app.db.redis import connect_redis, disconnect_redis
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_mongo()
    await connect_redis()
    await AuthService().ensure_indexes()
    await ChatService().ensure_indexes()
    yield
    await disconnect_redis()
    await disconnect_mongo()


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
async def spa_index() -> FileResponse:
    root_dir = Path(__file__).resolve().parents[1]
    return FileResponse(root_dir / "web" / "index.html")
