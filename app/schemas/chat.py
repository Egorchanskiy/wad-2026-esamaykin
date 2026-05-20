from datetime import datetime

from pydantic import BaseModel, Field


class ChatCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class AskRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    created_at: datetime


class AskResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
