# Verification and worktree safety

Verify the feature and its internationalization as one change. The exact command
set depends on the repository; discover scripts rather than inventing them.

## Preserve pre-existing work

Before writing:

1. Record `git status --short` and inspect existing diffs in files you may touch.
2. Do not overwrite user changes or treat them as generated noise.
3. For a narrow feature, edit around unrelated work and scope every diff command.
4. Before `sync`, `--sync-all`, bulk instrumentation, or unused-key cleanup, use
   a clean branch or isolated worktree unless all existing changes are part of
   the same task.
5. For a new language, snapshot existing locale directories so preservation can
   be checked after structural generation.

## Check resource integrity

For every changed locale resource:

- parse or import the file with its real format;
- compare key paths and container shapes to the primary catalog;
- compare interpolation, rich-text, nesting, formatting, and code-token sets;
- verify target-locale plural and context variants rather than copying the
  primary language's suffix assumptions;
- inspect the locale diff for rewritten non-empty values and formatting churn;
- distinguish absent structure from an empty pending translation.

Existing non-empty target values should remain identical unless the current
feature changed their meaning or the user requested retranslation.

## Run finite checks

Select the relevant repository-local commands:

```bash
rg --files -g 'i18next.config.*'
npx i18next-cli status
npx i18next-cli status de --hide-translated
npx i18next-cli status --unused
npx i18next-cli lint
npx i18next-cli extract --dry-run --ci
npx i18next-cli types --ci
```

If config discovery returns more than one path, identify the owning package and
repeat every applicable CLI command with `--config <selected-path>`. For a
read-only diagnosis, show both the discovery command and the selected path so
the result is reproducible.

For a scoped feature removal, `status --unused` is a review gate, not permission
for bulk deletion. If the local binary cannot run, document that limitation and
replace it with targeted searches over translation calls, nesting references,
tests, resource keys, and dynamic-key families. Report the review result before
claiming obsolete keys were removed safely.

The fallback review must distinguish and report all of these categories:

- direct calls and components such as `t("key")`, `i18next.t(...)`, and
  `<Trans i18nKey=...>`;
- nesting references such as `$t(...)` inside source and resource values;
- tests, fixtures, snapshots, and generated declarations;
- computed calls such as ``t(`errors.${code}`)`` and the complete resource
  family they can select;
- shared keys referenced outside the removed feature.

Use separate or clearly structured searches so an empty result is meaningful;
do not present one broad keyword search as proof for every category.

Then run the formatter on touched files, typecheck, focused tests, integration
tests, and build scripts defined by `package.json`. A failure that existed before
the task should be reported separately with evidence; do not hide it by changing
unrelated code or resources.

## Exercise runtime behavior

Test the languages, routes, and namespaces affected by the change:

- render the new or changed copy without raw keys or fallback surprises;
- test interpolation with realistic short, long, empty, and special-character
  values;
- test representative plural categories for each affected locale;
- inspect rich text, accessibility labels, validation messages, and layouts;
- verify formatted dates, numbers, currency, and lists use the active locale;
- for lazy resources, navigate directly and through client transitions;
- when language support changed, test selection, persistence, reload, routes,
  fallback, and switching back to existing languages.

## Review the final diff

The final change should contain only:

- requested application behavior;
- related translation calls and imports;
- primary and configured target values for affected keys;
- resource structure, runtime configuration, selector, route, or generated-type
  changes required by the task;
- directly relevant tests and snapshots.

If the task has no i18n impact, the final diff should contain none of those i18n
files. Report added, changed, renamed, and removed keys; translated locales;
preserved existing values; unresolved ambiguities; and remaining missing counts.
