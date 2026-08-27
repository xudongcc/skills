import { useTranslation } from "react-i18next";

export function ProfileForm() {
  const { t } = useTranslation("settings");

  return (
    <section>
      <h2>{t("profile.title")}</h2>
      <label>
        {t("profile.emailLabel")}
        <input type="email" name="email" />
      </label>
      <button type="submit">{t("actions.save")}</button>
    </section>
  );
}
