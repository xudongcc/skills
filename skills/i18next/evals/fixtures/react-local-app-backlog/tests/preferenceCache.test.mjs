import assert from "node:assert/strict";
import test from "node:test";

import {
  getCachedPreference,
  resetPreferenceCache,
  setCachedPreference,
} from "../src/preferenceCache.mjs";

test("isolates cached preferences by user", () => {
  resetPreferenceCache();
  setCachedPreference({ organizationId: "acme", userId: "alice" }, "compact");
  setCachedPreference({ organizationId: "acme", userId: "bob" }, "comfortable");

  assert.equal(
    getCachedPreference({ organizationId: "acme", userId: "alice" }),
    "compact",
  );
  assert.equal(
    getCachedPreference({ organizationId: "acme", userId: "bob" }),
    "comfortable",
  );
});

test("returns undefined for an uncached user", () => {
  resetPreferenceCache();
  assert.equal(
    getCachedPreference({ organizationId: "acme", userId: "unknown" }),
    undefined,
  );
});
