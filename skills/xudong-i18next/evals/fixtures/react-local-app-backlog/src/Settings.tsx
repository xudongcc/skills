import { useState } from "react";
import { useTranslation } from "react-i18next";

import { LanguageSelector } from "./LanguageSelector";
import { ProfileForm } from "./ProfileForm";

type SettingsProps = {
  errorCode?: "network" | "forbidden";
  onSaveNotifications: (enabled: boolean) => Promise<void>;
};

export function Settings({ errorCode, onSaveNotifications }: SettingsProps) {
  const { t } = useTranslation("settings");
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [savingNotifications, setSavingNotifications] = useState(false);

  async function saveNotifications() {
    setSavingNotifications(true);
    try {
      await onSaveNotifications(notificationsEnabled);
    } finally {
      setSavingNotifications(false);
    }
  }

  return (
    <main>
      <h1>{t("settings.title")}</h1>
      <LanguageSelector />
      <ProfileForm />

      <section data-testid="legacy-email-notifications">
        <h2>{t("notifications.title")}</h2>
        <p>{t("notifications.description")}</p>
        <label>
          <input
            type="checkbox"
            checked={notificationsEnabled}
            onChange={(event) => setNotificationsEnabled(event.target.checked)}
          />
          {t("notifications.enabled")}
        </label>
        <button
          type="button"
          disabled={savingNotifications}
          onClick={saveNotifications}
        >
          {savingNotifications ? t("actions.saving") : t("actions.save")}
        </button>
      </section>

      {errorCode ? <p role="alert">{t(`errors.${errorCode}`)}</p> : null}
    </main>
  );
}
