---
name: xudong-code-review
description: "Structured Codex code review when explicitly requested."
---

# Xudong Code Review

Run the bundled structured review helper only when the user explicitly asks for xudong-code-review or a Codex review.

Codex is the only supported engine. It uses `gpt-6.1-sol` with `high` reasoning by default and has no model fallback.

Do not invoke Xudong Code Review automatically before a commit, push, PR, merge, deploy, or final reply. Repository or workflow rules may call it only when they explicitly name it.

## Contract

- Default output includes P0 through P2 findings. Use `--max-priority P0` or
  `P1` to narrow the review, or `P3` when the caller explicitly asks for a wider review.
- Treat review output as advisory. Never blindly apply it.
- Verify every finding by reading the real code path and adjacent files.
- Read dependency docs/source/types when the finding depends on external behavior.
- Reject unrealistic edge cases, speculative risks, unrelated rewrites, and fixes that over-complicate the codebase.
- Prefer root-cause fixes at the right ownership boundary. A coherent refactor is appropriate when it removes the bug class, duplicate policy, stale paths, or ownership confusion; do not default to a symptom patch.
- When an accepted finding exposes a bug class or repeated pattern, inspect its owner and relevant sibling implementations before fixing.
- Fix the same bug class across its owner-boundary neighborhood when practical; stop at unrelated invariants, different owners, and unapproved contract changes.
- Run one bounded review pass. If an accepted finding changes code, run the smallest relevant test; rerun Xudong Code Review only when the user explicitly requests another pass.
- For security-audit suppression changes, verify accepted findings remain auditable: suppressed findings stay in structured output, active output keeps an unsuppressible suppression notice, and aggregate findings cannot hide unrelated active risk.
- Never switch or override the requested review model. Codex has no model fallback; access, capacity, rate-limit, and unrelated failures are returned directly.
- Be patient with large bundles. Structured review can take up to 30 minutes while the model call is active, especially with Codex tools or web search.
- Treat heartbeat lines like `review still running: ... elapsed=... pid=...` as healthy progress, not a hang. Let the helper continue while heartbeats are advancing. Pass `--stream-engine-output` when live engine text is useful; Codex filters tool/file chatter.
- Do not kill a review just because it has been quiet for 2-5 minutes, or because it is still running under the 30-minute window. Inspect the process only after missing multiple expected heartbeats, after 30 minutes, or after an obviously failed subprocess; prefer letting the same helper command finish.
- Tools are useful in review mode. Codex receives the validated bundle in an empty workspace so ignored files and linked-worktree metadata remain unreadable; web search stays available for dependency contracts and upstream docs.
- Security perspective is always included, but it should not cripple legitimate functionality. Report security findings only when the change creates a concrete, actionable risk or removes an important safety check.
- Reviewer subprocesses preserve engine authentication and non-credentialed proxy variables needed by headless or restricted-network environments while stripping process-injection, Git override, and credentialed proxy values.
- Immediately before every provider call, xudong-code-review writes the exact outgoing review pack to an owner-only temporary file and scans it with TruffleHog using `verified,unknown`. The scan covers prompt and dataset inputs, untracked content, and every diff line, including deleted lines. A finding, scanner error, or missing TruffleHog binary refuses the send and names the implicated repository file when it can be resolved; credentials are never redacted and forwarded. Security-sensitive paths remain omitted. Safe large diffs are sent as one pass while they fit the aggregate prompt limit, then partitioned into complete bounded passes without truncation.
- For regression provenance, keep roles separate: blamed code author, blamed PR author, PR merger/committer, current PR author, and PR/date. If no blamed PR is traceable, use the blamed commit as the provenance: commit SHA, date, and author username. Do not guess a merger or frame missing PR metadata as a separate finding.
- Do not invoke built-in `codex review`, nested reviewers, or review panels from inside the review. The helper builds one validated bundle, calls the selected engine once for normal inputs or once per complete bounded chunk for oversized inputs, validates the structured results, and stops.
- Stop as soon as the helper exits 0 with no accepted/actionable findings. Do not run an extra review just to get a nicer "clean" line, a second opinion, or clearer closeout wording.
- Treat the helper's successful exit plus absence of actionable findings as the clean review result, even if the underlying Codex CLI output is terse.
- If rejecting a finding as intentional/not worth fixing, add a brief inline code comment only when it explains a real invariant or ownership decision that future reviewers should know.
- Do not push just to review. Push only when the user requested push/ship/PR update.

## Scope

Xudong Code Review does not expand the task. Fix only verified blockers in the requested path. Mention unrelated findings without opening a new workstream, and stop when the requested review pass is complete.

## Skill Path

Invoke the installed script directly from the repository being reviewed. The
examples below use the global installation at `~/.agents/skills/xudong-code-review`.
For a project-local installation, replace that prefix with
`.agents/skills/xudong-code-review`; for a custom installation, use its actual path.

```bash
# Global installation:
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --help

# Project-local installation:
.agents/skills/xudong-code-review/scripts/xudong-code-review --help
```

On native Windows, run the extensionless helper with Python and use the
`test-review-harness.ps1` wrapper for the smoke harness, as shown below.

## Pick Target

Dirty local work:

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --mode local
```

Use this only when the patch is actually unstaged/staged/untracked in the
current checkout. `--mode uncommitted` is accepted as an alias for `--mode local`.
For committed, pushed, or PR work, point the helper at the commit
or branch diff instead; do not force dirty modes just
because the helper docs mention dirty work first. A clean local review
only proves there is no local patch.

Branch/PR work:

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --mode branch --base origin/main
```

Optional review context is first-class. Prompt files and datasets must be repo-relative so review bundles cannot pull arbitrary host files:

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --mode branch --base origin/main --prompt-file review-notes.md --dataset evidence.json
```

If an open PR exists, use its actual base:

```bash
base=$(gh pr view --json baseRefName --jq .baseRefName)
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --mode branch --base "origin/$base"
```

Committed single change:

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --mode commit --commit HEAD
```

Use commit review for already-landed or already-pushed work on `main`. Reviewing
clean `main` against `origin/main` is usually an empty diff after push. For a
small stack, review each commit explicitly or review the branch before merging
with `--base`.

## Oversized Bundles

The helper scans the full patch before partitioning it. A safe bundle that fits
the aggregate prompt limit remains one integrated review pass. Larger bundles
are split at bundle sections and file boundaries where possible; an oversized
single-file block is split at line boundaries with repeated file/hunk context
and an absolute new- or old-file line offset. Untracked snapshots use
injection-safe source-line records so continuation passes retain reportable
locations. A single physical diff line split across passes also retains its
original addition, deletion, or context marker.
Every original bundle byte appears exactly once across the pass sequence, and
all validated reports are merged before required-finding and exit-status checks.
The helper caps one run at eight bounded passes so an unexpectedly huge branch
cannot create unbounded model calls; split still-larger work into coherent review
targets.

Chunking makes large-diff review usable, but it cannot give one model call every
cross-file implementation detail. For architecture-heavy changes, still prefer
a coherent branch or PR shape whose semantic decision surface fits one pass.
Removing verified non-authoritative generated noise remains useful, but never
drop lockfiles, generated clients, policies, manifests, schemas, or other
independently semantic artifacts merely to shrink the review.

## Model and reasoning

Only Codex is supported. The default model is
`gpt-6.1-sol`, with `high` reasoning. Use `--model` or `--thinking` for an explicit
override. There is no automatic model fallback or `--fallback-model` option.
Access, capacity, rate-limit, and network failures are returned directly.

Accepted reasoning levels: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`.
The helper passes the level through `model_reasoning_effort`.

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --model gpt-6.1-sol --thinking high
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --codex-speed fast
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --codex-config 'model_verbosity="low"'
```

`--codex-speed` accepts `fast`, `flex`, and `default`; the selected model must
support the requested tier. Dedicated options take precedence over matching
`--codex-config` values. Config overrides accept only safe model/response tuning.

### Configuration

Review settings use fixed defaults and explicit CLI flags; configuration environment
variables and repository configuration files are not loaded. Defaults are
`gpt-6.1-sol`, `high` reasoning, P0 through P2 findings, no timeout, and no streamed
engine output. Use `--model`, `--thinking`, `--max-priority`,
`--engine-timeout-seconds`, `--stream-engine-output`, `--codex-config`, or
`--codex-speed` to override them. The executable is resolved as `codex` on `PATH`;
use `--codex-bin` for an explicit path. Authentication, proxy, and certificate
environment variables remain supported.

### Structured output and isolation

The helper supplies its JSON Schema through `--output-schema` and reads the
final report from `--output-last-message`. It parses and validates the report
before returning findings. Malformed output fails the review.

Codex runs in an empty temporary workspace with isolated HOME/XDG/runtime roots.
The validated bundle is its sole repository input. A named permission profile
allows filesystem reads only inside that workspace; ignored credentials and
linked-worktree metadata remain outside the readable boundary. Web search is
available unless `--no-web-search` is set. `--no-tools` is unsupported.

`--ignore-user-config` skips unrelated user configuration, `--ignore-rules` skips
user/project execpolicy rules, and project instructions, hooks, plugins, and MCP
servers are disabled. Only `cli_auth_credentials_store`, `forced_login_method`,
and `forced_chatgpt_workspace_id` are reconstructed from the external Codex
configuration to preserve authentication. File authentication is linked into the
isolated runtime so token refreshes remain durable; trusted keyring settings and
certificate paths are preserved without forwarding process-injection variables.

## Context Efficiency

Run the helper directly so target selection, engine choice, structured validation, and exit status all stay in one path. If output is noisy, summarize the completed helper output after it returns; do not ask another agent or reviewer to rerun the review.

## Helper

Show the helper options:

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --help
```

The smoke harness has thin shell wrappers over a shared Python implementation:

```bash
"$HOME/.agents/skills/xudong-code-review/scripts/test-review-harness" --fixture benign
```

On native Windows, invoke the extensionless Python helper through Python:

```powershell
python "$HOME/.agents/skills/xudong-code-review/scripts/xudong-code-review" --help
```

and the smoke harness:

```powershell
& "$HOME/.agents/skills/xudong-code-review/scripts/test-review-harness.ps1" -Fixture benign
```

The helper:

- chooses dirty local changes first
- accepts `--mode uncommitted` as an alias for `--mode local`
- otherwise uses current PR base if `gh pr view` works
- otherwise uses `origin/main` for non-main branches
- does not fetch automatically during branch review; the selected base ref must already resolve locally
- supports only Codex
- resolves bare `git`, `gh`, reviewer, and PowerShell shell commands from absolute `PATH` entries only, never from the reviewed checkout; explicit `--*-bin` paths are interpreted from the reviewed repository root when relative and accepted only when both the supplied path and resolved target stay outside the reviewed repository
- use `--mode commit --commit <ref>` for already-committed work, especially clean `main` after landing
- scans safe Git patches in full, recognizes synthetic fixture values tied to their credential field, reviews them in one pass up to the aggregate prompt limit, and automatically uses complete bounded passes above it
- should be left in `--mode auto` or forced to `--mode branch` for PR/branch work; do not force `--mode local` after committing
- writes only to stdout unless `--output`, `--json-output`, or live streamed engine stderr is set
- supports `--dry-run` (validates bundle construction, reviewer CLI resolution, and local isolation startup with a version probe without contacting a provider; exits nonzero if any check fails), an opt-in per-reviewer wall-clock bound via `--engine-timeout-seconds`, `--prompt`, repo-relative `--prompt-file`, repo-relative `--dataset`, `--no-web-search`, repeatable Codex-only safe model/response tuning with `--codex-config key=value`, Codex-only `--codex-speed fast|flex|default`, and commit refs
- supports `--stream-engine-output` for live engine text while preserving structured validation; Codex hides tool/file event details, emits compact activity summaries, and reports usage at turn completion
- uses `gpt-6.1-sol` with `high` reasoning and no model fallback; explicit `--model` and `--thinking` values override the built-in defaults
- gives Codex the validated bundle in an empty workspace with web search available
- prints `review still running: <engine> elapsed=<seconds>s pid=<pid>` to stderr at long-running intervals while waiting for the selected review engine, unless streamed output or compact Codex activity has been visible recently
- prints `xudong-code-review clean: no accepted/actionable findings reported` when the selected review command exits 0
- exits nonzero when accepted/actionable findings are present

## Final Report

Report material findings and the resulting status in chat. If there are none, say so plainly. Do not add command logs, test ledgers, proof blocks, or review receipts unless the user asks for them.
