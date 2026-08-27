import { defineConfig } from "i18next-cli";

export default defineConfig({
  locales: ["en", "de"],
  extract: {
    input: ["src/**/*.{ts,tsx}"],
    output: "locales/{{language}}/{{namespace}}.json",
    primaryLanguage: "en",
    secondaryLanguages: ["de"],
    defaultNS: "settings",
  },
});
