# Non-JavaScript and framework routing

`i18next-cli` parses `.js`, `.jsx`, `.ts`, and `.tsx` files by default. A glob
that includes another extension only selects the file; a plugin must parse and
transform that file type.

## Known plugins

The official CLI documentation currently lists these ecosystem plugins:

| Stack   | Package                                                                                                  | Purpose                                           |
| ------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Vue 2/3 | [`i18next-cli-vue`](https://github.com/PBK-B/i18next-cli-vue)                                            | Extract and instrument Vue single-file components |
| Svelte  | [`i18next-cli-plugin-svelte`](https://github.com/dreamscached/i18next-cli-plugin-svelte)                 | Extract keys from Svelte components               |
| Rsbuild | [`rsbuild-plugin-i18next-extractor`](https://github.com/rspack-contrib/rsbuild-plugin-i18next-extractor) | Extract resources through the Rspack module graph |

These packages are maintained outside the i18next CLI repository. Check their
current framework and CLI version compatibility before installing them, and
prefer the project's existing plugin when one is already configured.

For a standard CLI plugin, add the package to `plugins` in the local config:

```ts
import { defineConfig } from "i18next-cli";
import vue from "i18next-cli-vue";

export default defineConfig({
  locales: ["en", "de"],
  extract: {
    input: ["src/**/*.{js,ts,vue}"],
    output: "src/locales/{{language}}/{{namespace}}.json",
  },
  plugins: [vue()],
});
```

Inspect the selected plugin's README for its exact import and options; plugin
APIs can evolve independently of the CLI.

## Runtime bindings

Extraction and runtime rendering are separate concerns:

- React and Next.js projects commonly use `react-i18next` with `i18next`.
- Vue projects using i18next commonly use `i18next-vue`.
- Node.js services can load local files with `i18next-fs-backend`.
- Browser projects can bundle resources or load per-locale files from their own
  static assets with an appropriate i18next backend.

Before accepting generated instrumentation, verify that the runtime binding is
initialized at the correct application boundary and that changing language
causes the relevant components to render again. Pay particular attention to
server components, SSR hydration, and module-scope translation calls.

If the project uses a different i18n system, do not add i18next calls alongside
it automatically. Ask whether to keep the current system or plan an explicit
migration first.
