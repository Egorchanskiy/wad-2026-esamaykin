# API Structure

Base prefix: `/api/v1`

## Health

- `GET /health`

## Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me` (JWT access token required)
- `GET /auth/github/login`
- `GET /auth/github/callback?code=...`

## Chats and messages

- `POST /chats` - create chat
- `GET /chats` - list current working user chats
- `GET /chats/{chat_id}/messages` - full chat history
- `POST /chats/{chat_id}/messages` - add raw user message
- `POST /chats/{chat_id}/ask` - ask LLM, persist user+assistant messages
