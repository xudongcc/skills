# Permissions

Record concrete Feishu/Lark scopes that were actually required during real workflows. Prefer exact tool-returned scope names over memory or guesses.

## Known Required Scopes

### Message/history assisted bot lookup

When using user-authorized message/history APIs to inspect chat messages and recover a bot ID, the workflow required:

- `contact:user.basic_profile:readonly`

Observed behavior:

- `feishu_im_user_get_messages` returned an authorization prompt until this scope was granted.
- `feishu_im_user_search_messages` also prompted for authorization in the same workflow.

## Notes

- Tenant/application credentials alone may still be insufficient for some user-context message/history lookups.
- When a tool returns an authorization card, treat that card as the source of truth for missing scopes.
- Do not invent scopes from memory. If the tool does not expose the exact scope, record the exact error/prompt text instead.
- As this skill expands, append new sections here for send, search, directory, thread, or attachment-related scopes.
