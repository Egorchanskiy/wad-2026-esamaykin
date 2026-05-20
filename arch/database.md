# Database Structure

## MongoDB collections

### `users`

- `_id: ObjectId`
- `login: string` (unique)
- `password_hash: string` (for local auth users)
- `auth_provider: "local" | "github"`
- `github_id: string` (unique sparse index for GitHub users)
- `created_at: datetime`
- `updated_at: datetime`

Indexes:

- unique: `login`
- unique sparse: `github_id`

### `chats`

- `_id: ObjectId`
- `user_id: string` (owner user id)
- `title: string`
- `created_at: datetime`
- `updated_at: datetime`

Indexes:

- compound: `(user_id asc, updated_at desc)`

### `messages`

- `_id: ObjectId`
- `chat_id: string`
- `role: "user" | "assistant"`
- `content: string`
- `created_at: datetime`

Indexes:

- compound: `(chat_id asc, created_at asc)`

## Redis keys

Refresh token sessions:

- key format: `refresh:{user_id}:{token_id}`
- value: `"1"`
- TTL: `2592000` seconds (30 days by default)

## Note

You can find dull report in wad-2026-esamaykin.pdf
