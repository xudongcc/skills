# ID Lookup

Resolve Feishu/Lark IDs before sending native mentions or targeted messages. Separate the user path from the bot path because user-directory tools usually cannot discover bots.

## Cache files

- bot cache: `lark_bot_list.csv`
- user cache: `lark_user_list.csv`
- schema for both: `id,name`

Store both CSV files directly under the current OpenClaw Workspace.

If either file does not exist, create it with header:

```csv
id,name
```

## User ID lookup

Use this order:

1. if the current speaker is the target, trust `sender_id`
2. check `lark_user_list.csv`
3. call `feishu_get_user(user_id=..., user_id_type="open_id")` when an open_id is already known
4. call `feishu_search_user(query="...")` for name/email/phone lookup
5. call `feishu_chat_members(chat_id=...)` when the task is explicitly about members in a specific group
6. write confirmed `id,name` back into `lark_user_list.csv`

Notes:

- user cache is helpful, but weaker than bot cache because people can rename themselves and same-name collisions are more likely
- for the current speaker in a Feishu group, prefer inbound `sender_id` over name search

## Bot / agent ID lookup

Use this order:

1. check `lark_bot_list.csv`
2. call `feishu_chat.get(chat_id=...)` to confirm the chat and inspect bot-related metadata such as `bot_count`
3. call `feishu_im_user_get_messages(chat_id=..., sort_rule="create_time_desc", page_size=50)`
4. inspect:
   - `mentions[].id`
   - `mentions[].name`
   - sender fields where `sender_type = "app"` or equivalent bot/app metadata is present
5. if needed, call `feishu_im_user_search_messages(chat_id=..., sender_type="bot", page_size=50)`
6. write confirmed `id,name` back into `lark_bot_list.csv`

Notes:

- do not rely on `feishu_search_user` for bots
- do not rely on `feishu_chat_members` for bots
- the most stable bot ID source is an existing native @mention in message history

## Cache write-back rules

- ensure the cache file exists before writing
- update existing rows instead of creating duplicates for the same `id`
- preserve the exact ID string returned by Feishu; do not normalize or trim meaningful prefixes such as `ou_`
- if the same `name` maps to multiple ids, do not silently collapse them; prefer human confirmation or keep the existing confirmed row unchanged until clarified
