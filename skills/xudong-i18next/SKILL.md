---
name: xudong-i18next
description: "Use for implementation, review, diagnosis, and maintenance of localized user-facing behavior in JavaScript or TypeScript apps and services where i18next, react-i18next, or i18next-cli owns the affected package. Automatically maintain t()/Trans calls, semantic keys and namespaces, repository-local locale resources and missing translations, plural/interpolation/rich-text semantics, language onboarding/loading/selection/routing/fallback, generated types, and i18next-cli extraction/status/lint/sync/key renames as part of feature and copy work—even when the prompt does not mention internationalization. Also use for explicit i18next setup, adoption, or migration."
---

# Xudong i18next

Treat internationalization as part of normal feature development in an existing
i18next project. When a requested code change affects user-visible language,
maintain the source calls, local resources, translations, generated types, and
runtime behavior in the same change even if the user did not mention i18n.

Use `i18next-cli` as the repository-local static-analysis and resource tool, not
as the boundary of this skill. Follow the application's established runtime
binding and keep translation resources in the repository.

## Respect the task boundary

- A request to change or build authorizes the related i18n maintenance needed
  to complete that change. A review or diagnosis request remains read-only.
- Do not introduce i18next beside another localization system. Set up or migrate
  a project only when the user requests it.
- Do not add a language merely because the project could support one. Locale
  onboarding is an explicit product change.
- Preserve existing non-empty translations unless the user asks to revise them
  or their source meaning changed in the current task.
- If a change has no user-visible text, locale structure, language routing, or
  formatting impact, leave i18n files untouched and skip writing CLI commands.
- Do not turn a scoped feature into a cleanup of unrelated missing translations.
  Report pre-existing backlog separately when it affects verification.

## Read the relevant guidance

- Read [references/cli.md](references/cli.md) before configuring or running
  `i18next-cli`, extracting or renaming keys, synchronizing resources, checking
  unused keys, or generating types.
- Read [references/translating.md](references/translating.md) before writing
  translations, changing source meaning, or adding a language.
- Read [references/runtime.md](references/runtime.md) before changing runtime
  initialization, a language selector, namespace loading, SSR behavior, or a
  non-JavaScript framework integration.
- Read [references/verification.md](references/verification.md) before final
  verification or when the worktree already contains locale changes.

## Discover the project contract

Before editing, inspect enough of the repository to preserve its conventions:

1. Read `package.json`, the lockfile, package scripts, `git status`, and any
   repository instructions.
2. Locate `i18next.config.*` explicitly (for example with
   `rg --files -g 'i18next.config.*'`), plus runtime initialization, resource
   directories, generated declarations, language options, routes or middleware,
   and tests. When discovery finds multiple configs or the command runs outside
   the owning package, pass the selected path with `--config <path>` to every
   CLI check; do not rely on ambiguous auto-discovery.
3. Identify the primary and configured target languages, locale identifiers,
   namespaces, key and namespace separators, fallback policy, resource format,
   and whether resources are bundled or loaded dynamically.
4. Inspect nearby `t()`, `<Trans>`, hook, server, and test usage. Follow the
   existing framework boundary instead of inventing a second i18n pattern.
5. Determine which user-visible strings the requested change adds, changes, or
   removes. This impact list controls the i18n scope.

Do not require a perfectly clean repository for a small safe edit. Instead,
record the pre-existing state, avoid overlapping user changes, and use an
isolated worktree before any broad resource rewrite.

## Maintain i18n while developing

### Add user-visible behavior

1. Use the existing runtime binding and namespace for the owning feature.
2. Prefer a stable semantic key. Reuse a key only when the meaning, context, and
   lifecycle are genuinely the same.
3. Translate complete phrases. Use interpolation only for runtime values, the
   `count` option and target-locale plural variants for quantities, and
   `<Trans>` or the project's equivalent for rich component content.
4. Add or extract the primary value using the repository's established source
   of truth.
5. Fill every configured target language for keys introduced by the change.
   Use product context and preserve all i18next tokens and data shape.
6. Update generated resource types when configured.

### Change existing copy or behavior

Inspect every call site before deciding whether to retain a key:

- If wording changes but meaning remains stable, update the primary value and
  only the target values whose meaning must follow it.
- If meaning changes, create or rename to a semantic key and translate the new
  meaning. Do not silently keep a stale target translation merely because it is
  non-empty.
- If one shared key would now represent two meanings, split it and migrate only
  the affected call sites.
- A key that becomes apparently unused as a side effect of a scoped copy split
  is not automatically part of that change. Preserve it and report it as a
  cleanup candidate unless the task also authorizes removal and the unused-key
  review proves it is safe to delete.

Use `rename-key --dry-run` before applying a repository-wide key rename.

### Remove user-visible behavior

Remove associated translation calls and then run and review `status --unused`
before deleting resource keys. If the repository-local CLI is unavailable and
installing dependencies is outside the task, perform and report an equivalent
targeted review of translation call sites, nesting references, tests, resource
keys, and known dynamic-key families; record that the CLI check was unavailable.
Check and report each category explicitly—one generic text search is not enough
evidence of an unused-key review.
Delete a resource key only when that evidence shows it is no longer used.
Preserve shared or dynamically constructed keys when static analysis cannot
prove they are dead. Avoid enabling broad automatic deletion just to clean up
one feature.

### Make a change with no i18n impact

Keep locale resources, generated i18n types, runtime configuration, and
language selectors byte-for-byte unchanged. Normal code tests are sufficient;
do not manufacture i18n churn for completeness.

## Handle explicit maintenance tasks

For an incomplete locale, inventory it with a scoped status report and fill the
missing values directly. For a newly requested language, establish a clean
baseline, add it to both resource and runtime configuration, generate its
structure, translate it, and verify selection and fallback behavior. Follow
[references/translating.md](references/translating.md) for both workflows.

For a project with hardcoded strings and no established i18next setup, confirm
that introducing i18next is in scope. Preview instrumentation, review every
source transformation, configure local resources, fill the requested locales,
and test the initialized runtime.

## Verify the completed change

Verification should prove both the requested feature and its i18n maintenance:

1. Inspect the complete source, resource, configuration, and generated-type
   diff. Confirm unrelated locale values did not change.
2. Parse or load every changed resource and compare interpolation, rich-text,
   nesting, plural, context, and formatting tokens.
3. Run repository-owned verification scripts in their own finite command so
   optional CLI availability cannot hide or cancel their result.
4. Run scoped locale status, lint, non-writing extraction checks, and type
   generation checks as applicable. If a check is interrupted, rerun it
   separately before claiming it passed.
5. Run the project's formatter on touched files, typecheck, relevant tests, and
   build.
6. Exercise the affected UI in configured languages, including plural counts,
   rich text, formatted values, lazy namespaces, fallback, and persistence when
   relevant.
7. Report translated keys, removed keys, preserved existing translations,
   remaining ambiguities, and pre-existing failures separately.

End with finite checks. Watch mode can assist development but is not completion
evidence.

References: [i18next documentation](https://www.i18next.com/) and
[official i18next-cli repository](https://github.com/i18next/i18next-cli).
