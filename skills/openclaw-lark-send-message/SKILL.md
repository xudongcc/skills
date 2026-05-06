---
name: openclaw-lark-send-message
description: Use when a user asks to send a Feishu/Lark message, @mention a person or bot, test whether a group bot is reachable, find a Feishu bot/user open_id, recover a bot ID from chat history, or troubleshoot a Feishu mention that rendered as plain text.
---

# OpenClaw Lark Send Message

Use this skill for Feishu/Lark sends where exact recipients or native mentions matter. Identify target type, resolve a real Feishu ID, then send markup Feishu can parse.

## Core Rules

- First decide whether the target is a **user** or a **bot/agent**; lookup tools differ.
- Prefer native Feishu mention markup over plain-text `@name`.
- Store cache files directly under the current OpenClaw Workspace.
  - bot cache: `lark_bot_list.csv`
  - user cache: `lark_user_list.csv`
- If a cache file does not exist in that directory, create it with header `id,name` before writing.
- When a user or bot ID is recovered, append/update the appropriate cache file so future lookups can skip extra retrieval.
- Do **not** rely on `feishu_search_user` to find bots.
- Do **not** rely on `feishu_chat_members` to list bots; it does not return bot members.
- If a bot may already have spoken or been mentioned in the group, use message history to recover its ID.
- If Feishu asks for OAuth on message/history APIs, stop for authorization, then retry.

## Fast Workflow

1. Confirm the chat and target from conversation context. If either is ambiguous, ask one concise question.
2. Choose lookup path:
   - user: `sender_id` when the current speaker is the target, then user cache, then user lookup tools
   - bot/agent: bot cache, then chat/message history, then mention metadata
3. Read `references/id-lookup.md` when the ID is not already confirmed.
4. Send native mention markup using `references/mention.md`:

```text
<at user_id="OPEN_ID">DisplayName</at> 你的消息正文
```

Example:

```text
<at user_id="ou_example_bot_001">示例机器人</at> 联通测试，收到请回个 1。
```

5. Verify message metadata, native mention rendering, or the target's reply.

If the bot does not reply, separate these cases:

- mention formatting problem
- wrong bot ID
- bot is present but not configured to answer this trigger
- bot ignores bot-to-bot or group traffic

## Reference Routing

- Use `references/id-lookup.md` for cache setup, lookup order, and bot-vs-user ID recovery.
- Use `references/mention.md` for native mention formatting and verification.
- Use `references/permissions.md` when a tool returns an OAuth card, missing scope, or authorization prompt.
- Use `assets/*.example.csv` only as examples of cache schema; do not treat example IDs as real IDs.

## Permission Handling

When scope/authorization comes up, do not guess; use `references/permissions.md`.

## Output Style

- say whether the bot ID came from cache or from message-history recovery
- state the recovered ID when useful
- send the test message or say it is ready to send
- if blocked, say exactly which permission or input is missing
