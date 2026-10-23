import { useTranslation } from "react-i18next";

export const languageOptions = [
  { code: "en", label: "English" },
  { code: "de", label: "Deutsch" },
] as const;

export function LanguageSelector() {
  const { i18n, t } = useTranslation("settings");

  return (
    <label>
      {t("languageSelector.label")}
      <select
        value={i18n.resolvedLanguage ?? "en"}
        onChange={(event) => void i18n.changeLanguage(event.target.value)}
      >
        {languageOptions.map((language) => (
          <option key={language.code} value={language.code}>
            {language.label}
          </option>
        ))}
      </select>
    </label>
  );
}
