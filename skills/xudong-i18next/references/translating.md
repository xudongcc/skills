# Translating missing local resources

Use this guide when normal feature development introduces or changes copy, when
filling an incomplete locale, or when adding a language. The agent should write
the translations locally, preserve resource semantics, and leave a small review
list only for copy that cannot be translated reliably from available context.

## Establish the translation contract

Before editing, determine:

- primary and target locale codes, including region when it affects wording;
- namespaces and resource format (`json`, `json5`, `yaml`, JavaScript, or
  TypeScript);
- glossary, product names, tone, formality, capitalization, punctuation, and
  existing target-locale conventions;
- runtime fallback and language-selection behavior;
- whether the user wants only missing values filled or also wants existing
  translations reviewed.

Treat existing non-empty target translations as the strongest local style
evidence. During normal development, translate keys introduced or semantically
changed by the current task and do not expand into unrelated backlog. For an
explicit locale-completion request, fill the requested locale's entire backlog.

## Inventory and repair structure

Run a scoped report first:

```bash
npx i18next-cli status de --hide-translated
```

The target locale can contain:

- **empty values**: the key exists and needs a translation;
- **absent values**: the catalog structure is incomplete and should be repaired
  before translating;
- **translated values**: preserve them unless retranslation was requested.

If keys are absent, first confirm that the source and existing locale resources
are current with `extract --dry-run --ci`. Run `sync` only in a clean or isolated
worktree because it aligns every secondary locale to the primary catalog and
removes obsolete keys. Inspect the structural diff before writing translations.

## Translate with context

For each missing value, use this evidence in order:

1. the primary-language value and full key path;
2. the source call or component that renders the key;
3. interpolation parameters, count/context usage, and surrounding UI;
4. glossary, style guide, README, product documentation, and tests;
5. nearby translations in the same namespace and existing target-locale copy.

Translate clear UI copy directly. For a genuinely ambiguous term, inspect more
source context; if it remains ambiguous and the choice materially affects
meaning, leave it unresolved and report the exact key with the competing
interpretations.

When primary wording changes, determine whether its meaning also changed. Keep
an existing target value only if it still expresses the same meaning. A
non-empty but now-stale translation is not complete.

## Preserve i18next semantics

- Keep interpolation names and delimiters exactly, for example `{{name}}` and
  `{{count}}`. Translate the surrounding grammar, not the variable identifier.
- Keep rich-text/component placeholders such as `<0>...</0>`, `<1>`, or named
  tags balanced and semantically unchanged.
- Keep nested translation references such as `$t(other.key)` intact unless the
  referenced key itself is intentionally renamed.
- Translate every required plural and ordinal variant as a complete natural
  phrase. Use the variants generated for the target locale; do not assume all
  languages use only `_one` and `_other`.
- Keep context variants consistent while preserving the grammatical distinction
  represented by the suffix.
- Preserve keys, namespaces, object/array shape, scalar types, escaping, and
  formatting supported by the existing resource file.
- Keep URLs, identifiers, brand names, keyboard shortcuts, and code tokens
  unchanged unless project context explicitly localizes them.
- Do not copy the primary text into the target locale merely to make status pass.

## Work in reviewable batches

Translate one locale and preferably one namespace at a time. For a feature
change, keep the batch scoped to affected keys across every configured target
locale. After each batch:

1. parse or load the resource file to catch syntax errors;
2. inspect the diff for changed existing values, key churn, placeholder loss,
   and unexpected formatting;
3. compare placeholder and rich-text token sets between primary and target;
4. run the scoped status report again.

Finish with:

```bash
npx i18next-cli status de --hide-translated
npx i18next-cli lint
npx i18next-cli extract --dry-run --ci
npx i18next-cli types --ci
```

Also run the project's typecheck, tests, build, and a runtime language-switch
smoke test. Report translated key count, remaining missing keys, ambiguous keys,
and whether existing translations were preserved.

## Add a language safely

For an existing localized application:

1. Establish a clean baseline: current extraction and types checks pass, and
   existing locales have no unexpected resource drift.
2. Add the new locale to `locales` and any explicit `secondaryLanguages` in
   `i18next.config.*`.
3. Update the runtime's supported languages, resource loader, routes or
   middleware, language detector, selector UI, and persistence rules as
   applicable.
4. Run `sync` to create the new locale's key skeleton. Stop if the diff changes
   existing non-empty translations or unrelated files.
5. Translate the new locale using the rules above, then regenerate configured
   types and verify the runtime can select and load it.
