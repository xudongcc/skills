# Mention

Send native Feishu/Lark mentions only after the target ID is known.

Before resolving a mention target, read `id-lookup.md` and follow its lookup order for users or bots.

## Native mention format

Use:

```text
<at user_id="OPEN_ID">DisplayName</at> 你的消息正文
```

`OPEN_ID` must be the exact Feishu ID recovered from cache, lookup, or message history. `DisplayName` is only the rendered label; it cannot make a plain-text `@name` behave like a native mention.

Examples:

```text
<at user_id="ou_example_bot_001">示例机器人</at> 联通测试，收到请回个 1。
```

```text
<at user_id="ou_xxx">张三</at> 麻烦看一下这个 MR。
```

## Verification

After sending, verify one of these:

- the sent message contains native mention metadata in history
- the target replies
- the current chat visibly renders a native @mention instead of plain-text `@name`

## Common mistakes

- sending plain-text `@名字` and assuming it is a native mention
- trying to mention a bot before recovering its ID
- using user directory lookup for bot targets instead of the message-history path in `id-lookup.md`
- using example IDs from `assets/*.example.csv` in real messages
