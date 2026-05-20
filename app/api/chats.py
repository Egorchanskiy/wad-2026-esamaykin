from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.chat import (
    AskRequest,
    AskResponse,
    ChatCreateRequest,
    ChatResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.chat_service import ChatService
from app.services.llm_service import LlmService

router = APIRouter(prefix="/chats", tags=["chats"])


def _chat_to_response(chat: dict) -> ChatResponse:
    return ChatResponse(
        id=str(chat["_id"]),
        title=chat["title"],
        created_at=chat["created_at"],
        updated_at=chat["updated_at"],
    )


def _message_to_response(message: dict) -> MessageResponse:
    return MessageResponse(
        id=str(message["_id"]),
        chat_id=message["chat_id"],
        role=message["role"],
        content=message["content"],
        created_at=message["created_at"],
    )


@router.post("", response_model=ChatResponse)
async def create_chat(
    payload: ChatCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatResponse:
    chat = await ChatService().create_chat(str(current_user["_id"]), payload.title)
    return _chat_to_response(chat)


@router.get("", response_model=list[ChatResponse])
async def list_chats(current_user: dict = Depends(get_current_user)) -> list[ChatResponse]:
    chats = await ChatService().list_chats(str(current_user["_id"]))
    return [_chat_to_response(chat) for chat in chats]


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    chat_id: str,
    current_user: dict = Depends(get_current_user),
) -> list[MessageResponse]:
    try:
        messages = await ChatService().list_messages(chat_id, str(current_user["_id"]))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return [_message_to_response(msg) for msg in messages]


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def add_message(
    chat_id: str,
    payload: MessageCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    chat_service = ChatService()
    chat = await chat_service.get_chat(chat_id, str(current_user["_id"]))
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    message = await chat_service.add_message(chat_id, "user", payload.content)
    return _message_to_response(message)


@router.post("/{chat_id}/ask", response_model=AskResponse)
async def ask_llm(
    chat_id: str,
    payload: AskRequest,
    current_user: dict = Depends(get_current_user),
) -> AskResponse:
    chat_service = ChatService()
    llm_service = LlmService()
    chat = await chat_service.get_chat(chat_id, str(current_user["_id"]))
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    user_message = await chat_service.add_message(chat_id, "user", payload.prompt)
    answer = await llm_service.ask(payload.prompt)
    assistant_message = await chat_service.add_message(chat_id, "assistant", answer)
    return AskResponse(
        user_message=_message_to_response(user_message),
        assistant_message=_message_to_response(assistant_message),
    )
