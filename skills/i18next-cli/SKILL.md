---
name: i18next-cli
description: "Use when working with local i18next translation resources through i18next-cli: initializing config, extracting keys, syncing locale files, checking translation status, generating TypeScript types, migrating i18next-parser configs, renaming translation keys, or linting and instrumenting hardcoded strings in JavaScript, TypeScript, React, Vite, Next.js, or similar projects."
---

# i18next CLI

Use `i18next-cli` as the source of truth for repository-local i18next resource
maintenance. Keep translation resources in the project and prefer CLI-generated
changes over hand-editing generated locale or type files.

This workflow manages i18next resources and source instrumentation. It does not
replace the application's runtime i18next setup or write finished translations
for the user.

## Prepare

1. Locate the project root that owns `i18next.config.ts`,
   `i18next.config.js`, or the translation resources.
2. Read `package.json`, the lockfile, existing package scripts, runtime i18n
   initialization, and `git status` before changing anything.
3. Confirm Node.js 22 or newer. Current `i18next-cli` releases require it.
4. Prefer an existing package script. Otherwise run the locally installed
   binary with the detected package manager (`pnpm exec`, `npm exec --`,
   `yarn`, or `bunx`). Examples below use `npx` only as shorthand.
5. If the CLI is not installed, add `i18next-cli` as a development dependency
   with the project's package manager. Do not install it globally.

If the project uses another i18n library, stop before instrumenting or migrating.
Changing runtime libraries is a separate decision that can alter routing,
rendering, and translation-key semantics.

## Configure local resources

If there is no config, run the interactive initializer and select **Local files
only**, or create the config directly when the requested locales and paths are
already known:

```bash
npx i18next-cli init
```

```ts
import { defineConfig } from "i18next-cli";

export default defineConfig({
  locales: ["en", "de"],
  extract: {
    input: ["src/**/*.{js,jsx,ts,tsx}"],
    output: "public/locales/{{language}}/{{namespace}}.json",
  },
});
```

Inspect at least `locales`, `extract.input`, `extract.output`,
`primaryLanguage`, `defaultNS`, and `removeUnusedKeys`. The extractor owns the
files matched by `extract.output`; keep manually maintained files outside that
output pattern.

For a legacy `i18next-parser` project, preview the existing config and then run:

```bash
npx i18next-cli migrate-config
# Or provide a non-default legacy config path:
npx i18next-cli migrate-config config/i18next-parser.config.mjs
```

Review the generated config before running extraction.

## Diagnose before writing

Start with read-only analysis whenever possible:

```bash
npx i18next-cli status
npx i18next-cli status de --hide-translated
npx i18next-cli status --unused
npx i18next-cli lint
npx i18next-cli extract --dry-run
npx i18next-cli types --ci
```

`extract --ci` can still update resource files before returning its status. Use
`extract --dry-run --ci` for a check that must not modify the worktree, or run
the normal CI form only in an isolated checkout.

Use `--config <path>` or `-c <path>` when the config is outside the current
working directory or a monorepo contains more than one config.

## Instrument hardcoded strings

Instrumentation is a heuristic first pass, so require a reviewable working tree
and preview it before applying changes:

```bash
npx i18next-cli instrument --dry-run
npx i18next-cli instrument --interactive
```

After instrumentation:

1. Inspect every source diff for false positives, missed strings, broken
   interpolation or pluralization, module-scope calls, and framework-specific
   server/client boundaries.
2. Review any generated i18n initialization file and install the runtime
   dependencies it names. The CLI may add imports or initialization code, but
   it does not install those runtime packages.
3. Run the application's typecheck and relevant tests before extracting.
4. Run `extract` only after the source changes are acceptable.

The built-in parser handles `.js`, `.jsx`, `.ts`, and `.tsx`. Read
[references/stacks.md](references/stacks.md) before processing Vue, Svelte, or
other file types; adding an extension to `extract.input` is not sufficient.

## Maintain resources

Extract keys and optionally refresh types in the same run:

```bash
npx i18next-cli extract
npx i18next-cli extract --with-types
```

Use synchronization options deliberately:

```bash
# Update the primary locale from explicit default values in code.
npx i18next-cli extract --sync-primary

# Also clear synchronized entries in secondary locales.
npx i18next-cli extract --sync-all

# Align secondary locale key structure with the primary locale.
npx i18next-cli sync
```

`--sync-all`, `sync`, and `removeUnusedKeys: true` can create broad locale
churn. Run in a clean or isolated worktree, inspect the diff, and preserve
translator-authored values unless the user explicitly requested the rewrite.
Use `--trust-derived` only when defaults inferred from keys or `keyPrefix` are
acceptable.

Generate or verify TypeScript definitions:

```bash
npx i18next-cli types
npx i18next-cli types --ci
```

Rename a key across source and resource files with a preview first:

```bash
npx i18next-cli rename-key 'checkout.pay' 'checkout.submit' --dry-run
npx i18next-cli rename-key 'checkout.pay' 'checkout.submit'
```

## Verify

After any write command:

1. Inspect `git diff`, including generated resource and type files.
2. Run `status` and the relevant locale-specific detail view.
3. Run `extract --dry-run --ci` and `types --ci` when configured.
4. Run the project's typecheck, tests, and build that exercise the localized UI.
5. Report missing translations separately from structural or extraction errors;
   the CLI can identify missing values but does not author approved copy.

Use `--watch` only during an interactive development session. End with finite
verification commands so the final result is reproducible.

Reference: [official i18next-cli repository](https://github.com/i18next/i18next-cli).
