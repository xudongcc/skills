# Repository-local i18next CLI workflow

Use `i18next-cli` for static analysis, resource structure, key refactors, status,
linting, and generated types. The application runtime and the translation values
remain part of the surrounding development task.

## Prepare the command

1. Confirm Node.js 22 or newer for current CLI releases.
2. Read the lockfile and prefer an existing package script.
3. Otherwise run the locally installed binary with the detected package manager:
   `pnpm exec`, `npm exec --`, `yarn`, or `bunx`.
4. When dependency installation is outside the task, confirm that the local
   binary or installed package exists before invoking a package runner. Do not
   let `npx`, `npm exec`, or an equivalent runner download or resolve a missing
   package; report the CLI checks as unavailable instead.
5. Add `i18next-cli` as a development dependency only when the project needs it
   and dependency installation is within the task scope. Do not install it
   globally.
6. Pass `--config <path>` or `-c <path>` when automatic discovery is ambiguous,
   especially in a monorepo.

Examples below use `npx` as shorthand; substitute the repository's actual
runner.

Run repository-owned verification scripts separately from these CLI commands.
A missing or stalled optional CLI invocation must not erase the evidence from
the project's tests, typecheck, build, or resource-integrity scripts.

## Configure local resources

If no configuration exists, use the interactive initializer's local-resource
path or create the known configuration directly:

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

Inspect `locales`, `extract.input`, `extract.output`, `primaryLanguage`,
`secondaryLanguages`, `defaultNS`, separators, `removeUnusedKeys`, namespace
ignores, and status ignores. Files matched by `extract.output` are owned by the
catalog workflow; keep unrelated hand-maintained data outside that pattern.

For an `i18next-parser` project, preview and migrate its existing configuration:

```bash
npx i18next-cli migrate-config
npx i18next-cli migrate-config config/i18next-parser.config.mjs
```

Review the generated configuration before extraction.

## Diagnose without writing

Use these commands selectively:

```bash
npx i18next-cli status
npx i18next-cli status de --hide-translated
npx i18next-cli status --namespace settings
npx i18next-cli status --unused
npx i18next-cli lint
npx i18next-cli extract --dry-run --ci
npx i18next-cli types --ci
```

`status` treats absent primary keys as errors while tolerating deliberate empty
primary placeholders. For a secondary locale, both absent and empty required
values are incomplete; the detailed view distinguishes them. Optional
locale-specific plural variants may be reported without failing completion.

`status --unused` never writes, but static analysis cannot prove that a key built
dynamically at runtime is unused. Treat its output as candidates for review, not
an unconditional deletion list.

`extract --ci` can write files before returning its result. Use
`extract --dry-run --ci` when the worktree must remain unchanged.

## Update resources deliberately

After source calls are correct, preview extraction and inspect its proposed
scope:

```bash
npx i18next-cli extract --dry-run
npx i18next-cli extract
npx i18next-cli extract --with-types
```

Use synchronization flags only for their intended contract:

```bash
# Refresh primary values from explicit defaults in source.
npx i18next-cli extract --sync-primary

# Refresh primary values and clear synchronized secondary entries.
npx i18next-cli extract --sync-all

# Align every secondary locale's structure to the primary locale.
npx i18next-cli sync
```

`--sync-all`, `sync`, and `removeUnusedKeys: true` can produce broad locale
changes. Run them in a clean or isolated worktree, inspect all affected locales,
and preserve translator-authored values. Use `--trust-derived` only when values
inferred from keys or key prefixes are acceptable primary copy.

Generate or check declarations after resources stabilize:

```bash
npx i18next-cli types
npx i18next-cli types --ci
```

## Rename and remove keys

Preview a key refactor across source and resources:

```bash
npx i18next-cli rename-key 'common:checkout.pay' 'common:checkout.submit' --dry-run
npx i18next-cli rename-key 'common:checkout.pay' 'common:checkout.submit'
```

Keep namespace prefixes and inspect every changed call site and locale value.
For deletion, start with `status --unused`, then verify nested references and
dynamic key families before removing a key. Avoid a broad sync solely to delete
one resource entry.

## Instrument existing source

Instrumentation is a heuristic first pass:

```bash
npx i18next-cli instrument --dry-run
npx i18next-cli instrument --interactive
```

Review false positives, missed strings, template literals with expressions,
interpolation and plural handling, module-scope calls, imports, and server/client
boundaries. Confirm the generated initialization matches the application's
loading model and run source tests before extraction.

The built-in parser handles `.js`, `.jsx`, `.ts`, and `.tsx`. Other file types
need a compatible plugin; read [runtime.md](runtime.md) before extending the
input glob.
