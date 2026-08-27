# Runtime and framework integration

Use the application's existing i18next instance, binding, loading architecture,
and language state. Resource maintenance is incomplete if the changed copy
cannot resolve in the runtime where it is rendered.

## Inspect the runtime contract

Locate and understand:

- the initialized i18next instance and framework adapter;
- bundled resources, dynamic imports, filesystem backend, or HTTP backend;
- `supportedLngs`, `fallbackLng`, namespaces, default namespace, separators,
  and language normalization;
- detector, URL, cookie, storage, or application-state persistence;
- selector options, localized routes or middleware, and document language;
- SSR preload, hydration, server/client boundaries, and tests.

Preserve the existing fallback and persistence policy unless the requested
feature changes it.

## Use complete translatable units

- Put complete sentences and labels in one translation value. Avoid joining
  translated fragments or interpolating words that translators need to inflect.
- Use interpolation for values known only at runtime, preserving parameter names.
- Pass `count` for cardinal plurals and use the target locale's required CLDR
  variants. Test representative zero, one, two, few, many, and other cases as
  applicable.
- Use `<Trans>` or the binding's equivalent when components or markup occur
  inside a sentence. Keep numbered or named tags balanced across locales.
- Format dates, numbers, currency, lists, and relative time with the active
  locale through the existing i18next or `Intl` formatting path.
- Preserve default escaping behavior. If escaping is disabled for a framework
  that already escapes output, do not extend that assumption to raw HTML or
  untrusted content.

## React and Vite

Follow the established `react-i18next` pattern:

- use `useTranslation(namespace)` inside function components;
- use `<Trans>` for nested React elements rather than splitting sentences;
- keep hook calls inside React component or custom-hook boundaries;
- make statically imported or dynamically loaded resources mirror the same
  namespace shape for every configured language;
- ensure changing language causes affected components to render again.

Do not introduce a second i18next instance or mix synchronous module-scope
translations into a runtime that loads resources asynchronously.

## Next.js and server rendering

Determine whether the project uses the Pages Router, App Router, server
components, client components, or a repository-specific server translation
helper. Preserve that architecture:

- do not add client-only hooks to a server component;
- preload the route's language and namespaces before server rendering;
- keep server and client locale resolution consistent to avoid hydration drift;
- update locale route or middleware allowlists only when supported languages
  change;
- verify direct navigation, client navigation, reload, and fallback behavior.

Generated instrumentation must be reviewed especially carefully at these
boundaries.

## Node.js and services

Prefer an instance whose resources are ready before request handling or message
formatting. In concurrent services, avoid mutating one global language for
multiple requests; use fixed translators or isolated instances according to the
existing architecture. Verify filesystem paths and production packaging for
local resources.

## Add a namespace

Create a namespace when it matches an ownership or loading boundary, not merely
because a file is growing. Update all configured locales, static resource maps
or backend paths, preload lists, generated types, and route tests. Confirm the
namespace loads before its first translation call and does not fall back to raw
keys during loading.

## Add a language

When explicitly requested:

1. Use a consistent BCP 47 locale identifier in the CLI config, resource path,
   runtime allowlist, detector normalization, routes, selector, persistence, and
   document metadata.
2. For bundled resources, register every namespace for the new language. For a
   backend, verify the existing load path resolves the new files.
3. Preserve the established fallback language.
4. Add the language endonym to the selector following its existing data model.
5. Test selection, reload, navigation, fallback, and switching back to every
   existing language.

## Non-JavaScript source formats

`i18next-cli` parses `.js`, `.jsx`, `.ts`, and `.tsx` by default. A glob that
includes another extension selects the file but does not parse it; use a
compatible plugin and check its current framework and CLI support.

Examples listed by the CLI ecosystem include:

| Stack   | Package                                                                                                  | Purpose                                           |
| ------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Vue 2/3 | [`i18next-cli-vue`](https://github.com/PBK-B/i18next-cli-vue)                                            | Extract and instrument Vue single-file components |
| Svelte  | [`i18next-cli-plugin-svelte`](https://github.com/dreamscached/i18next-cli-plugin-svelte)                 | Extract keys from Svelte components               |
| Rsbuild | [`rsbuild-plugin-i18next-extractor`](https://github.com/rspack-contrib/rsbuild-plugin-i18next-extractor) | Extract through the Rspack module graph           |

Prefer a plugin already configured by the project. Inspect its current README
before adding or changing it because plugin APIs evolve separately.

If the project uses a different runtime localization system, do not add i18next
calls beside it. Treat migration as a separate explicit change.
