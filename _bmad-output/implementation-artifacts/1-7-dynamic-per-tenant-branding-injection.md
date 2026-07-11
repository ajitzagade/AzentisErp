---
baseline_commit: ece3a97
---

# Story 1.7: Dynamic Per-Tenant Branding Injection

Status: done

## Story

As a tenant's staff user,
I want the page to reflect my business's colors and logo immediately after an admin changes them,
so that branding updates don't require anyone to touch a server.

## Acceptance Criteria

1. Given Tenant Settings' `primary_color` is changed and saved, when the next page loads, then the new color renders as an inline CSS custom property — no `bench build`, no restart (FR8, AD-3).
2. Given Tenant Settings has no record yet or a malformed one, when a page loads, then it fails open to stock/default branding rather than breaking the page (spine's fail-open convention), and no per-tenant compiled CSS file is ever written to disk (AD-3's explicit prohibition).
3. Given `login_background` is changed (set, cleared, or swapped) and saved, when the login page next loads, then it reflects the change immediately — the same live-injection, no-restart rule Story 1.3 relies on applies identically to the background image, not just colors.

## Dev Notes — Read Before Starting

**This story closes the loop Story 1.3 explicitly deferred and Story 1.6 explicitly declined to wire.** Story 1.3's `our_brand.css` already declares `:root { --tenant-primary: #6d28d9; --tenant-secondary: #06b6d4; --tenant-on-primary: #ffffff; }` as hardcoded platform defaults, and a `--login-background-image` custom-property hook that the mesh background's `var()` fallback already reads (proven working in Story 1.3 via a manually-set test value). Story 1.6 built `Tenant Settings` and `our_brand.utils.get_tenant_settings()` but wired nothing to consume it. This story is what actually connects live Tenant Settings data to those existing CSS hooks — it does not invent new CSS structure.

**Chosen mechanism: a whitelisted JSON API + a small runtime JS file, not a Jinja template injection.** Investigated (during Story 1.3) whether a Jinja context hook (`update_website_context`) could inject computed values into `login.html`'s rendered `<head>`, and concluded there's no safe injection point without overriding `login.html` wholesale (its `head_include` block is fully replaced by login.html itself, no `super()` call) or overriding the much more central `base.html`/`web.html` (high blast-radius, against the minimal-footprint pattern this project has followed in every prior story). Decision: skip server-side HTML injection entirely.
- New whitelisted, guest-accessible API method, `our_brand.api.get_branding()` (`@frappe.whitelist(allow_guest=True)` — must be guest-accessible since the login page itself, a pre-auth surface, needs it). Reads `our_brand.utils.get_tenant_settings()` (Story 1.6's accessor — this is now its first real consumer) and returns a small JSON object: `primary_color`, `secondary_color`, `on_primary` (computed via `our_brand.utils.contrast_text_color()`, Story 1.3's function — this is now its first real per-render caller, exactly as anticipated in Story 1.3's Completion Notes), `login_background`. **Only include a key in the response when Tenant Settings actually has a truthy value for it** — omission, not a defaulted/null value, is the fail-open signal the frontend relies on (AC2).
- New JS file, `our_brand/public/js/branding.js`, wired via **both** `app_include_js` (desk) and `web_include_js` (login/web pages) — on load, calls the API and, for each key present in the response, calls `document.documentElement.style.setProperty("--tenant-x", value)`. Never calls `setProperty` for an absent key. Wrapped so any fetch/parse failure is silently swallowed — the CSS file's own hardcoded `:root` defaults (Story 1.3) are the fallback, and since JS only *overrides* those defaults when it has real data, "do nothing on failure" is inherently fail-open, no explicit error-handling branch needs to duplicate the default values.
- **Why this satisfies AD-3's "inline CSS custom property, injected via a page-load hook, never a compiled per-tenant asset file" literally**: `style.setProperty` on `document.documentElement` *is* setting an inline custom property (visible as `style="--tenant-primary: ...`" on `<html>` in devtools); the JS file itself is one static platform-wide asset (already compiled once, same for every tenant) — no per-tenant file is ever written to disk, satisfying the explicit prohibition in AC2.
- **`login_background`**: when present, JS sets `--login-background-image: url("...")` — the exact custom property Story 1.3's mesh CSS already has a `var()` fallback for. When absent (not set, or cleared), the property is never set, so the CSS fallback (the mesh gradients) applies automatically — no explicit "clear" logic needed, verified this is how the Story 1.3 mechanism already behaves.

**Fail-open for a missing/malformed Tenant Settings record (AC2)**: `get_tenant_settings()` (Story 1.6) always returns *a* doc — Single DocTypes never 404, an unsaved Single just returns field defaults (empty strings/None). `our_brand.api.get_branding()` must treat empty/None color fields as "not set" (omit from response), and wrap the luminance computation in Dev Notes' established `contrast_text_color()` — that function already only accepts two hex strings, so guard the call itself: if `primary_color`/`secondary_color` aren't both present and parseable as hex, omit `on_primary` too rather than letting a malformed value raise and 500 the whole endpoint (a 500 response would still be handled gracefully by the JS's fetch-failure fallback, but a clean 200-with-omitted-keys is the more correct fail-open behavior per the AC's own wording — "fails open... rather than breaking the page," implying the page load itself shouldn't even see an error).

### Previous Story Intelligence (1.1–1.6)

- `our_brand/public/js/splash_retry.js` (Story 1.4) is the existing precedent for a small vanilla-JS file wired via `app_include_js` — follow the same style (IIFE, no framework dependency).
- `our_brand/utils.py` already has `contrast_text_color()` (Story 1.3) and `get_tenant_settings()` (Story 1.6) — this story is their first real consumer, add `our_brand/api.py` alongside, don't duplicate either function.
- Verification method: `bench --site dev.local console` to set real Tenant Settings values and call `our_brand.api.get_branding()` directly (bypassing HTTP) for the fail-open/data-shape checks; authenticated + guest curl against the whitelisted HTTP endpoint (`/api/method/our_brand.api.get_branding`) to confirm it's actually guest-reachable (critical — the login page is unauthenticated, an endpoint that silently requires auth would break AC1/AC3 there specifically); curl the login/desk pages for the `<script>` tag confirming `branding.js` is linked.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile; `bench build --app our_brand` needed for new JS.

## Tasks / Subtasks

- [x] Task 1: Create the whitelisted branding API (AC: 1, 2, 3)
  - [x] Created `our_brand/our_brand/api.py::get_branding()`, `@frappe.whitelist(allow_guest=True)`
  - [x] Reads Tenant Settings via `our_brand.utils.get_tenant_settings()`; response includes `primary_color`/`secondary_color`/`on_primary` only when both colors are valid hex (regex-checked), `login_background` only when truthy
- [x] Task 2: Create the runtime branding JS (AC: 1, 2, 3)
  - [x] Created `our_brand/our_brand/public/js/branding.js` — fetches `our_brand.api.get_branding`, sets only the CSS custom properties present in the response via `document.documentElement.style.setProperty`, swallows all fetch/parse failures silently
  - [x] Wired via both `app_include_js` (now a list: `splash_retry.js` + `branding.js`) and `web_include_js` in `hooks.py`
- [x] Task 3: Build and verify (AC: all)
  - [x] `bench build --app our_brand` — succeeded
  - [x] Guest curl against `/api/method/our_brand.api.get_branding` (no auth) → `200 {"message":{}}` with Tenant Settings empty, confirming both guest-accessibility and AC2's fail-open default
  - [x] **Real bug found and fixed during verification (not in the story's actual implementation code)**: first attempt to set test Tenant Settings values via `frappe.get_cached_doc("Tenant Settings")` + `.save()` raised `CannotChangeConstantError: Value cannot be changed for Created By` and silently did NOT persist to the DB (confirmed via a fresh `frappe.clear_cache()` + re-fetch) — even though the same in-process console session's later `get_branding()` call appeared to return the new values, because it was reading the same mutated-but-unsaved in-memory cached object, not the DB. Root cause: `get_cached_doc()` is a read-optimized accessor and misbehaves as a write target on a Single record's first-ever save. **This confirms AD-2's own division of labor was correct all along** — the accessor is for reads only; `get_branding()` (this story's actual code) only ever reads via it, never writes, so this bug was in my verification script's methodology, not in any shipped code. Fixed the test by using `frappe.get_doc("Tenant Settings")` (fresh, uncached) for the write, which persisted correctly.
  - [x] Re-verified: fresh `frappe.get_doc()` read after the corrected save showed the real persisted values; guest curl against `get_branding()` (same running process, no rebuild/restart between the save and the curl) immediately reflected `{"primary_color":"#E1562F","secondary_color":"#C81D6B","on_primary":"#FFFFFF","login_background":"/files/test-bg.png"}` — AC1 and AC3's "no bench build, no restart" requirement directly confirmed
  - [x] curl `/login` and authenticated `/app` — `branding.js` `<script src="/assets/our_brand/js/branding.js">` confirmed present on both
  - [x] Confirmed no per-tenant compiled CSS file exists anywhere under `sites/`/`public/` — only the one platform-wide `our_brand/our_brand/public/css/our_brand.css` (AC2's explicit prohibition)
  - [x] Reset Tenant Settings back to empty after verification; re-curled the guest endpoint to confirm it returned to `{}` (fail-open state restored, no leftover test data)
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `curl .../api/method/our_brand.api.get_branding` (guest, empty Tenant Settings) → `200 {"message":{}}`
- Console: `frappe.get_cached_doc("Tenant Settings")` + `.save()` → `CannotChangeConstantError: Value cannot be changed for Created By`, values did NOT persist (confirmed via fresh `frappe.clear_cache()` + re-fetch showing `None`)
- Console: `frappe.get_doc("Tenant Settings")` (uncached) + `.save()` → succeeded, fresh re-fetch confirmed persisted values
- `curl .../api/method/our_brand.api.get_branding` (guest, real values set, same running process, no rebuild) → `200 {"primary_color":"#E1562F","secondary_color":"#C81D6B","on_primary":"#FFFFFF","login_background":"/files/test-bg.png"}`
- curl `/login` and authenticated `/app` → both show `<script src="/assets/our_brand/js/branding.js">`
- Reset console script → confirmed guest endpoint back to `{}`
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **The `get_cached_doc()`-as-write-target bug was a verification-methodology mistake, not a defect in shipped code** — worth recording clearly since it could otherwise read as a story-blocking bug. `our_brand/api.py::get_branding()` (the actual deliverable) only ever calls `get_tenant_settings()` (Story 1.6's read-only accessor) — it never writes. The bug only appeared because my *test script* took a shortcut and tried to reuse the same cached-read accessor for a write, which AD-2's own text never sanctioned ("every read path... through the accessor" — writes were always expected to go through a normal `frappe.get_doc()`/`.save()`). Caught by verifying against a fresh, uncached re-fetch rather than trusting the same in-process object's apparent success.
- **Chose a JS+API mechanism over a Jinja context-injection mechanism**, a decision made during Story 1.3's investigation and confirmed still correct here: no frappe/erpnext template needed to be touched at all for this story, since `document.documentElement.style.setProperty` from a page-load script satisfies AD-3's "inline CSS custom property, injected via a page-load hook" requirement literally, without the block-override complications a Jinja-based approach would have hit (documented in Story 1.3's Dev Notes).
- **Fail-open is structurally guaranteed, not defensively coded**: because the JS only *overrides* CSS custom properties that already have hardcoded defaults in `our_brand.css` (Story 1.3), and only when the API response actually contains a key, both a network failure (JS `.catch()`) and a malformed/empty Tenant Settings record (API omits the key) collapse to the same safe behavior — the CSS file's own defaults render, unmodified. Verified both paths independently (empty Tenant Settings via the API test, and implicitly the JS fetch-failure path by code inspection since simulating a network failure wasn't practical via curl-based verification).
- Closes the loop explicitly left open by Stories 1.3 and 1.6: `contrast_text_color()` (1.3) and `get_tenant_settings()` (1.6) both predicted a future real caller in their own Completion Notes — this story is that caller for both.
- No automated test framework, consistent with all prior Epic 1 stories' documented decision.

### File List

- `myerp/apps/our_brand/our_brand/api.py` (new — `get_branding()`)
- `myerp/apps/our_brand/our_brand/public/js/branding.js` (new)
- `myerp/apps/our_brand/our_brand/hooks.py` (modified — `app_include_js` now a list, `web_include_js` added)

## Review Findings (2026-07-11)

Consolidated code review covering Stories 1.2-1.7 (see each story's own file for story-specific context; this section records findings and patches specific to this story's code). Three parallel reviewers (Blind Hunter, Edge Case Hunter, Acceptance Auditor) ran twice — the first pass used an incomplete diff (plain `git diff` silently excludes untracked new files, so Stories 1.3-1.7's new files were invisible to it); a corrected diff including untracked files was constructed and the review re-run. See `deferred-work.md`'s "Deferred from: code review of stories 1.2-1.7" entry for the process note and all deferred (non-blocking) findings.

**Patches applied (3, all in this story's code):**

1. **`get_branding()` all-or-nothing color bug (AC1 violation)** — found independently by all three reviewers. `get_branding()` required both `primary_color` and `secondary_color` to be valid hex before returning *either* one, so a tenant who set only `primary_color` (a scenario AC1's own wording explicitly describes) got no live update at all — the page silently kept the platform-default color. Fixed: each color is now included independently when individually valid; `on_primary` is still only computed when both are present (a gradient needs two stops), which is a reasonable, undocumented-but-sensible scope boundary since AC1 doesn't require contrast-perfect single-color states.
2. **Not actually fail-open despite AC2's explicit requirement** — Edge Case Hunter found two unhandled crash paths in the same function: a 3-digit hex shorthand (`#fff`) passed the original regex but would raise inside `contrast_text_color()`'s luminance slicing, and any exception from `get_tenant_settings()` itself was completely unguarded. Both would 500 the guest-facing login page instead of failing open. Fixed: `HEX_COLOR_RE` now requires exactly 6 hex digits (matching what `contrast_text_color()` actually expects), and the entire function body is wrapped in try/except returning `{}` on any unexpected error.
3. **Unescaped CSS injection risk in `login_background`** — Blind Hunter found `branding.js` concatenated the server-returned `login_background` value directly into a `url("...")` CSS custom property with no escaping, while `api.py` only checks it for truthiness (no format validation, unlike the regex-checked color fields). Fixed: `branding.js` now escapes backslashes and double-quotes before embedding the value in the CSS string token.

All three patches verified via `bench --site dev.local console` (single-color case now returns `{'primary_color': '#E1562F'}`; 3-digit-hex case now returns only the other valid color with no crash; both-valid case unchanged) and a guest curl confirming the endpoint still returns `{}`/200 in the fail-open default state after `bench build --app our_brand`.

**Dismissed as false positive**: the hardcoded `#2684ff` focus-ring outline color, flagged by Blind Hunter as an "unbranded" color — this is intentional per `EXPERIENCE.md`'s explicit accessibility requirement for a fixed, non-tenant-color-dependent focus outline.

**Deferred (non-blocking, logged to `deferred-work.md`)**: per-tenant email branding fields unused, per-tenant logo/favicon fields unused (both by-design for Epic 1's platform-wide scope), `login_background` blur/opacity not suppressed for a real photo, several Email Account lifecycle edge cases in `install.py`, no rollback of pre-existing `Website Settings` values on uninstall, Jinja `ChoiceLoader` install-order fragility, `after_install`-only-runs-once provisioning gap, `contrast_text_color()`'s average-luminance limitation, missing `TenantSettings.validate()`, two dead logo asset files from Story 1.2, no rate limiting on the guest-accessible branding endpoint.
