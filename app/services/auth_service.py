from datetime import UTC, datetime

import httpx
from jose import JWTError, jwt
from pymongo.errors import DuplicateKeyError

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.db.mongo import get_db
from app.db.redis import get_redis
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def users_collection(self):
        return get_db()["users"]

    async def ensure_indexes(self) -> None:
        await self.users_collection.create_index("login", unique=True)
        await self.users_collection.create_index("github_id", unique=True, sparse=True)

    async def register(self, login: str, password: str) -> TokenResponse:
        now = datetime.now(UTC)
        user_doc = {
            "login": login,
            "password_hash": hash_password(password),
            "auth_provider": "local",
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self.users_collection.insert_one(user_doc)
        except DuplicateKeyError as exc:
            raise ValueError("Login already exists") from exc
        user_id = str(result.inserted_id)
        return await self._issue_tokens(user_id)

    async def login(self, login: str, password: str) -> TokenResponse:
        user = await self.users_collection.find_one({"login": login})
        if not user or user.get("auth_provider") != "local":
            raise ValueError("Invalid credentials")
        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        return await self._issue_tokens(str(user["_id"]))

    async def login_with_github_code(self, code: str) -> TokenResponse:
        if not self.settings.github_client_id or not self.settings.github_client_secret:
            raise ValueError("GitHub OAuth is not configured")

        access_token = await self._exchange_github_code(code)
        github_user = await self._fetch_github_user(access_token)
        user = await self._get_or_create_github_user(github_user)
        return await self._issue_tokens(str(user["_id"]))

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = self._decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token type")
        user_id = payload.get("sub")
        token_id = payload.get("jti")
        if not user_id or not token_id:
            raise ValueError("Invalid refresh token payload")

        redis_key = self._redis_refresh_key(user_id, token_id)
        stored = await get_redis().get(redis_key)
        if stored != "1":
            raise ValueError("Refresh session expired or revoked")

        await get_redis().delete(redis_key)
        return await self._issue_tokens(user_id)

    async def logout(self, refresh_token: str) -> None:
        payload = self._decode_token(refresh_token)
        if payload.get("type") != "refresh":
            return
        user_id = payload.get("sub")
        token_id = payload.get("jti")
        if user_id and token_id:
            await get_redis().delete(self._redis_refresh_key(user_id, token_id))

    async def get_user_by_id(self, user_id: str) -> dict | None:
        from bson import ObjectId

        try:
            object_id = ObjectId(user_id)
        except Exception:
            return None
        return await self.users_collection.find_one({"_id": object_id})

    async def _exchange_github_code(self, code: str) -> str:
        url = "https://github.com/login/oauth/access_token"
        payload = {
            "client_id": self.settings.github_client_id,
            "client_secret": self.settings.github_client_secret,
            "code": code,
            "redirect_uri": self.settings.github_redirect_uri,
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        token = data.get("access_token")
        if not token:
            raise ValueError("Failed to obtain GitHub access token")
        return token

    async def _fetch_github_user(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://api.github.com/user", headers=headers)
            response.raise_for_status()
        data = response.json()
        if not data.get("id"):
            raise ValueError("Failed to fetch GitHub profile")
        return data

    async def _get_or_create_github_user(self, github_user: dict) -> dict:
        github_id = str(github_user["id"])
        existing = await self.users_collection.find_one({"github_id": github_id})
        if existing:
            return existing

        base_login = github_user.get("login") or f"github_{github_id}"
        login = base_login
        suffix = 1
        while await self.users_collection.find_one({"login": login}):
            suffix += 1
            login = f"{base_login}_{suffix}"

        now = datetime.now(UTC)
        doc = {
            "login": login,
            "auth_provider": "github",
            "github_id": github_id,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self.users_collection.insert_one(doc)
        except DuplicateKeyError:
            return await self.users_collection.find_one({"github_id": github_id})
        doc["_id"] = result.inserted_id
        return doc

    async def _issue_tokens(self, user_id: str) -> TokenResponse:
        access_token = create_access_token(user_id)
        refresh_token, token_id = create_refresh_token(user_id)

        await get_redis().setex(
            self._redis_refresh_key(user_id, token_id),
            self.settings.refresh_token_ttl_seconds,
            "1",
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def _decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise ValueError("Invalid token") from exc

    @staticmethod
    def _redis_refresh_key(user_id: str, token_id: str) -> str:
        return f"refresh:{user_id}:{token_id}"
