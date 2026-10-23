import { readFile, readdir } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const localesRoot = join(projectRoot, "locales");
const locales = (await readdir(localesRoot, { withFileTypes: true }))
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
const localePaths = Object.fromEntries(
  locales.map((locale) => [locale, join(localesRoot, locale, "settings.json")]),
);

function flatten(value, prefix = "", output = new Map()) {
  for (const [key, child] of Object.entries(value)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (child && typeof child === "object" && !Array.isArray(child)) {
      flatten(child, path, output);
    } else {
      output.set(path, child);
    }
  }
  return output;
}

function tokens(value) {
  return [...String(value).matchAll(/{{[^{}]+}}|<\/?[A-Za-z0-9]+>/g)]
    .map((match) => match[0])
    .sort();
}

const catalogs = Object.fromEntries(
  await Promise.all(
    Object.entries(localePaths).map(async ([locale, path]) => [
      locale,
      flatten(JSON.parse(await readFile(path, "utf8"))),
    ]),
  ),
);

function quotedValues(source, pattern, label) {
  const match = source.match(pattern);
  if (!match) throw new Error(`could not read ${label}`);
  return [...match[1].matchAll(/["']([^"']+)["']/g)]
    .map((item) => item[1])
    .sort();
}

function assertSameValues(actual, expected, label) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(
      `${label} ${JSON.stringify(actual)} does not match locale directories ${JSON.stringify(expected)}`,
    );
  }
}

const [configSource, runtimeSource, selectorSource] = await Promise.all([
  readFile(join(projectRoot, "i18next.config.ts"), "utf8"),
  readFile(join(projectRoot, "src/i18n.ts"), "utf8"),
  readFile(join(projectRoot, "src/LanguageSelector.tsx"), "utf8"),
]);

assertSameValues(
  quotedValues(configSource, /locales\s*:\s*\[([^\]]+)\]/, "CLI locales"),
  locales,
  "CLI locales",
);
assertSameValues(
  quotedValues(
    runtimeSource,
    /supportedLanguages\s*=\s*\[([^\]]+)\]/,
    "runtime languages",
  ),
  locales,
  "runtime languages",
);
assertSameValues(
  [
    ...runtimeSource.matchAll(
      /^\s{4}([A-Za-z][\w-]*)\s*:\s*\{\s*settings\s*:/gm,
    ),
  ]
    .map((match) => match[1])
    .sort(),
  locales,
  "runtime resources",
);
assertSameValues(
  [...selectorSource.matchAll(/\bcode\s*:\s*["']([^"']+)["']/g)]
    .map((match) => match[1])
    .sort(),
  locales,
  "language selector",
);

const enKeys = [...catalogs.en.keys()].sort();
for (const [locale, catalog] of Object.entries(catalogs)) {
  const localeKeys = [...catalog.keys()].sort();
  if (JSON.stringify(localeKeys) !== JSON.stringify(enKeys)) {
    throw new Error(`${locale} key structure does not match English`);
  }

  for (const key of enKeys) {
    const value = catalog.get(key);
    if (typeof value !== "string" || value.trim() === "") {
      throw new Error(`${locale}:${key} is not a completed string`);
    }
    if (
      JSON.stringify(tokens(value)) !==
      JSON.stringify(tokens(catalogs.en.get(key)))
    ) {
      throw new Error(`${locale}:${key} changed protected tokens`);
    }
  }
}

const sourceRoot = join(projectRoot, "src");
const sourceFiles = (await readdir(sourceRoot, { withFileTypes: true }))
  .filter((entry) => entry.isFile() && /\.(?:ts|tsx)$/.test(entry.name))
  .map((entry) => join(sourceRoot, entry.name));

for (const path of sourceFiles) {
  const source = await readFile(path, "utf8");
  const label = relative(projectRoot, path);

  for (const match of source.matchAll(/\bt\(\s*["']([^"']+)["']/g)) {
    const key = match[1];
    const pluralPrefix = `${key}_`;
    if (
      !catalogs.en.has(key) &&
      ![...catalogs.en.keys()].some((candidate) =>
        candidate.startsWith(pluralPrefix),
      )
    ) {
      throw new Error(`${label} references absent key ${match[1]}`);
    }
  }

  for (const match of source.matchAll(
    /<Trans\b[^>]*\bi18nKey=["']([^"']+)["']/g,
  )) {
    if (!catalogs.en.has(match[1])) {
      throw new Error(`${label} references absent Trans key ${match[1]}`);
    }
  }

  const hardcodedText = source.match(/>\s*([A-Za-z][^<{]*?)\s*<\/[A-Za-z]/);
  if (hardcodedText) {
    throw new Error(
      `${label} contains hardcoded JSX text: ${hardcodedText[1]}`,
    );
  }

  const hardcodedAttribute = source.match(
    /\b(?:aria-label|placeholder|title|alt)=["']([A-Za-z][^"']*)["']/,
  );
  if (hardcodedAttribute) {
    throw new Error(
      `${label} contains hardcoded user-facing attribute: ${hardcodedAttribute[1]}`,
    );
  }
}

console.log(`i18n integrity passed for ${enKeys.length} settings keys`);
