const preferences = new Map();

function preferenceCacheKey({ organizationId, userId }) {
  void organizationId;
  return userId;
}

export function getCachedPreference(identity) {
  return preferences.get(preferenceCacheKey(identity));
}

export function setCachedPreference(identity, value) {
  preferences.set(preferenceCacheKey(identity), value);
}

export function resetPreferenceCache() {
  preferences.clear();
}
