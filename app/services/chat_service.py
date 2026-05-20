from datetime import UTC, datetime

from bson import ObjectId

from app.db.mongo import get_db


class ChatService:
    @property
    def chats_collection(self):
        return get_db()["chats"]

    @property
    def messages_collection(self):
        return get_db()["messages"]

    async def ensure_indexes(self) -> None:
        await self.chats_collection.create_index([("user_id", 1), ("updated_at", -1)])
        await self.messages_collection.create_index([("chat_id", 1), ("created_at", 1)])

    async def create_chat(self, user_id: str, title: str) -> dict:
        now = datetime.now(UTC)
        doc = {
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.chats_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def list_chats(self, user_id: str) -> list[dict]:
        cursor = self.chats_collection.find({"user_id": user_id}).sort("updated_at", -1)
        return await cursor.to_list(length=100)

    async def get_chat(self, chat_id: str, user_id: str) -> dict | None:
        object_id = self._to_object_id(chat_id)
        if object_id is None:
            return None
        return await self.chats_collection.find_one({"_id": object_id, "user_id": user_id})

    async def add_message(self, chat_id: str, role: str, content: str) -> dict:
        now = datetime.now(UTC)
        chat_object_id = self._to_object_id(chat_id)
        if chat_object_id is None:
            raise ValueError("Invalid chat id")

        doc = {
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "created_at": now,
        }
        result = await self.messages_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        await self.chats_collection.update_one(
            {"_id": chat_object_id},
            {"$set": {"updated_at": now}},
        )
        return doc

    async def list_messages(self, chat_id: str, user_id: str) -> list[dict]:
        chat = await self.get_chat(chat_id, user_id)
        if not chat:
            raise ValueError("Chat not found")
        cursor = self.messages_collection.find({"chat_id": chat_id}).sort("created_at", 1)
        return await cursor.to_list(length=1000)

    @staticmethod
    def _to_object_id(value: str) -> ObjectId | None:
        try:
            return ObjectId(value)
        except Exception:
            return None
