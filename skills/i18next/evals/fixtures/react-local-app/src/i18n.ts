import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import deSettings from "../locales/de/settings.json";
import enSettings from "../locales/en/settings.json";

export const supportedLanguages = ["en", "de"] as const;

void i18n.use(initReactI18next).init({
  resources: {
    en: { settings: enSettings },
    de: { settings: deSettings },
  },
  supportedLngs: supportedLanguages,
  fallbackLng: "en",
  defaultNS: "settings",
  interpolation: { escapeValue: false },
});

export default i18n;
