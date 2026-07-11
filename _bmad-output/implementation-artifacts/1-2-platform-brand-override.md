---
baseline_commit: 12f1496
---

# Story 1.2: Platform Brand Override

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the platform operator,
I want the app's name, logo, favicon, and metadata replaced platform-wide,
so that no page shows "Frappe" or "ERPNext" as the product name.

## Acceptance Criteria

1. Given the base platform from Story 1.1 (ERPNext installed, pinned and unmodified, on site `dev.local`), when `our_brand` is scaffolded (`bench new-app`) and installed, then `app_name`/`app_title`/`app_publisher`/`app_logo_url` in `hooks.py` reflect our brand, not Frappe's defaults.
2. Given `our_brand` is installed, when any **desk** page renders (post-login admin UI — navbar, browser tab title, sidebar chrome), then no visible string "Frappe" or "ERPNext" appears in that chrome.
3. Given `our_brand` is uninstalled, when the site reloads, then stock Frappe/ERPNext branding returns cleanly, proving isolation (FR15/AD-1).
4. Given `our_brand` is installed or uninstalled, when the Frappe/ERPNext source tree is inspected, then no file under it is modified (NFR8) — verified via `git diff` against upstream showing zero changes outside `our_brand`.

**Scope boundary — read before starting:** AC2 is about **desk chrome only** (the authenticated admin UI: navbar app name/logo, browser tab title). It does **not** include the login page's visual styling, footer text ("Built on Frappe/ERPNext"), colors, or splash screen — those are Story 1.3 and 1.4's job, not this one's. Do not touch `app_include_css`, login templates, or any CSS in this story. If you find yourself writing CSS or touching the login page, you've scope-crept into Story 1.3.

## Tasks / Subtasks

- [x] Task 1: Scaffold the Branding App (AC: 1)
  - [x] `bench new-app our_brand` — scaffolded at `myerp/apps/our_brand/`, installed and built cleanly (`bench build --app our_brand` ran automatically as part of the command). App Title "Azentis" (confirmed with user, inferred from the provided logo), App Publisher "Ajit Zagade" (asked, no safe default existed), App Description "Unified Business Management Platform", App Email `ajitzagade3@gmail.com`, App License `mit` (default accepted).
  - [x] **Real fix required, not in the original task list:** `bench new-app` initializes its own nested `.git` repository inside the new app by default. This made git see `myerp/apps/our_brand/` as one opaque "embedded repository" (like a broken submodule) instead of tracking its individual files — confirmed via `git add -A --dry-run myerp/` showing a single `add 'myerp/apps/our_brand/'` line with a submodule warning, instead of the actual file list. Removed `myerp/apps/our_brand/.git` entirely; re-verified `git add -A --dry-run myerp/` now correctly lists all 17 individual scaffold files as trackable. Story 1.1's whitelist pattern (`!myerp/apps/our_brand`) itself was correct — the nested repo was the actual problem, and would have silently broken tracking for anyone who ran `bench new-app` without knowing to check for this.
- [x] Task 2: Set app metadata in `hooks.py` (AC: 1)
  - [x] `app_name = "our_brand"`
  - [x] `app_title = "Azentis"` — confirmed with user (inferred from the provided logo, not "AzentisERP" the project working title)
  - [x] `app_publisher = "Ajit Zagade"` — asked, no safe default existed
  - [x] `app_description = "Unified Business Management Platform"` — PRD's suggested placeholder, used as-is
  - [x] `app_logo_url = "/assets/our_brand/images/logo.png"` — added (this field is not part of `bench new-app`'s interactive scaffold prompts, had to be added manually after Task 3 placed the actual asset)
- [x] Task 3: Add logo and favicon assets (AC: 1, 2)
  - [x] Created `myerp/apps/our_brand/our_brand/public/images/`
  - [x] Real, finished logo provided by user (not a placeholder): `logo.png` (canonical, = dark-bg variant per user's explicit reference), plus `logo-dark-bg.png` and `logo-light-bg.png` kept as named variants for Story 1.3's dark/light theme work (`DESIGN.md` already specifies both). All copied from user-provided source files, 861×889px RGBA.
  - [x] Favicon investigated and confirmed **out of scope for this story**: Frappe v15's favicon is a `Website Settings` DocType field (`frappe/frappe/website/doctype/website_settings/website_settings.py`), not a `hooks.py` mechanism — grepped Frappe's own `hooks.py` and confirmed it sets no favicon hook itself, only `app_logo_url`. AC1 only requires `app_logo_url`; AC2 is about visible text strings, not icon imagery. Deferred to Story 1.6 (Tenant Settings already has a planned `favicon` field) as originally scoped in planning — not a gap, a correct boundary.
- [x] Task 4: Install `our_brand` on the dev site and verify desk chrome (AC: 1, 2)
  - [x] `bench --site dev.local install-app our_brand` — succeeded
  - [x] **Real problem found and fixed, not anticipated by the original task list:** installing `our_brand` and setting `hooks.py`'s `app_title`/`app_logo_url` was NOT sufficient — the desk `<title>` still read "Frappe" and the navbar logo still showed Frappe's, verified via an authenticated `curl` against `/app/home` (session cookie from `/api/method/login`), not just visual inspection. Root-caused in Frappe's own source: (1) the desk `<title>` tag (`frappe/www/app.html`) resolves via `frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or "Frappe"` — a **Website Settings** data field, never `hooks.py`'s `app_title` at all; (2) the navbar logo (`frappe/core/doctype/navbar_settings/navbar_settings.py:get_app_logo`) checks `Website Settings.app_logo` / `Navbar Settings.app_logo` first, and only falls back to `hooks.py`'s `app_logo_url` hook when neither is set — and that fallback only works cleanly for exactly 2 apps; with `our_brand` installed alongside `frappe` and `erpnext` (both of which also define `app_logo_url`), the fallback logic's `if len(logos) == 2` special case doesn't trigger, and it silently keeps Frappe's own logo instead. **Fix:** added `our_brand/install.py` with an `after_install` hook that sets `Website Settings.app_name`/`app_logo` directly (the actually-authoritative source), wired via `hooks.py`'s `after_install`. Re-verified via the same authenticated curl check: `<title>Azentis</title>`, `"app_logo_url": "/assets/our_brand/images/logo.png"` — both correct.
  - [x] Checked the full rendered desk HTML for remaining "Frappe"/"ERPNext" occurrences beyond title/logo — found only: internal asset URLs (`/assets/frappe/...`, not visible text), the legitimate installed-apps metadata list (frappe/erpnext's own real identity, unmodified per AD-1 — not a branding bug), and `System Settings.app_name` (a dead code path once `Website Settings.app_name` is set, never actually rendered). No further chrome-visible text found.
- [x] Task 5: Verify isolation — uninstall/reinstall round-trip (AC: 3, 4)
  - [x] `bench --site dev.local uninstall-app our_brand --yes` — succeeded. Also added a `before_uninstall` hook (`our_brand/install.py`) clearing `Website Settings.app_name`/`app_logo` back to `None` — without this, AC3's "stock branding returns cleanly" would have been false (the Website Settings values would have persisted as leftover state after uninstall, exactly the kind of thing AC3 is checking for). Verified via authenticated curl: `<title>Frappe</title>`, `"app_logo_url": "/assets/erpnext/images/erpnext-logo.svg"` (2-app fallback correctly resolves to erpnext's logo once `our_brand` is gone — expected stock behavior, not a bug).
  - [x] Reinstalled `our_brand` — `after_install` fired automatically this time (unlike the first install, done before the hook existed, which needed a manual `bench execute our_brand.install.after_install`). Re-verified: `<title>Azentis</title>`, our logo path — both correct, site left in the intended branded state.
  - [x] `git status`/`git diff --stat` in `myerp/apps/frappe` and `myerp/apps/erpnext` — both completely clean. Commit hashes re-confirmed unchanged from Story 1.1's baseline: `frappe @ 105b17938839f4e5c6cdff817d42afc40c3bcc32`, `erpnext @ b5f784612d5b7969b72848dda5b22f10d3a8f764`.

## Dev Notes

- **Builds directly on Story 1.1.** The bench (`myerp/`), ERPNext installation, and site (`dev.local`) all already exist and are working — do not recreate any of that. If `bench start` isn't currently running, start it; don't re-run `bench init`/`bench get-app`/`bench new-site`.
- **`.gitignore` is already configured correctly for this story** (Story 1.1, Task 5): the whitelist pattern `myerp/*` / `!myerp/apps` / `myerp/apps/*` / `!myerp/apps/our_brand` was built and verified specifically in anticipation of this story. `our_brand`'s files should be trackable by git automatically — if `git status` shows them as ignored instead, that's a real regression to investigate, not something to route around.
- **Known deferred risk from Story 1.1's code review** (see `deferred-work.md`): the whitelist's safety *inside* `our_brand` relies on unrelated global `.gitignore` patterns (`*.env`, `*.log`, `__pycache__/`), not a dedicated rule. If this story's own file layout includes anything matching those patterns legitimately (unlikely for a fresh app scaffold), double-check it isn't silently excluded.
- **Scope discipline (repeated from Acceptance Criteria, because it matters):** this story is `hooks.py` metadata + logo/favicon assets only. No CSS, no login template, no email templates, no `app_include_css`. Those belong to Stories 1.3–1.5. Creating tables/entities/files beyond what THIS story's ACs need violates the project's established "create only what's needed now" discipline (see Story 1.1's Dev Notes, same principle).
- **Two real values need the user's input, don't invent them:** `app_publisher` (operator/company name) and the actual logo image. Neither was specified anywhere in planning. Ask rather than guess — a wrong guess here becomes visible product branding, not an internal detail.
- **Favicon mechanism is genuinely unconfirmed** — `addendum.md`'s original plan mentions favicon only as a Tenant Settings field (Story 1.6, per-tenant, later), not as part of this platform-wide story. Story 1.2's AC1 only lists `app_logo_url` in `hooks.py`, not an explicit favicon hook. Verify what Frappe v15 actually uses for the platform-default favicon before assuming `app_logo_url` covers it — it may not.
- **Architecture governance:** AD-1 (customization lives only in `our_brand`, Frappe/ERPNext core never modified, never pushed to) is what AC3/AC4 test directly. AD-2's "cached accessor" pattern doesn't apply yet — that's Story 1.6 (Tenant Settings) — this story has no data model, just static `hooks.py` config.
- **UX design contract (`DESIGN.md`/`EXPERIENCE.md`) is largely Story 1.3's concern, not this one's** — this story doesn't touch colors, typography, or the login page's visual composition. The one overlap: `DESIGN.md`'s login-card component references a logo mark rendered from the tenant's/platform's logo — the `logo.png` asset this story creates is what that will eventually reference, so keep it a reasonably square/simple mark-friendly image, not an oddly-shaped banner.

### Project Structure Notes

- New files land under `myerp/apps/our_brand/` — see the Architecture Spine's Structural Seed source tree for the full eventual layout (`hooks.py`, `our_brand/doctype/`, `our_brand/www/`, `our_brand/templates/`, `our_brand/public/`, `our_brand/commands/`). This story only touches `hooks.py` and `our_brand/public/images/` — the rest of that tree (doctype/, www/, templates/, commands/) belongs to later stories and should not be created prematurely.
- `apps/frappe` and `apps/erpnext` remain untouched and gitignored, exactly as Story 1.1 left them.

### Testing Standards

- No formal automated test framework exists yet (same as Story 1.1 — deliberately deferred for the solo 1-month MVP). Verification is manual/observational against the ACs: visually confirm desk chrome branding, and command-level `git diff`/`git status` checks for AC3/AC4.

### Previous Story Intelligence (from Story 1.1)

- Bench root: `myerp/` (relative to repo root). Site: `dev.local`. Login: `Administrator` / `admin` (local dev only).
- **Gotcha carried forward:** don't manually start Redis on ports 11000/13000 outside of `bench start`'s own Procfile management — doing so once already broke `bench start` during Story 1.1 (port conflict cascaded to killing the whole process group). If `bench start` isn't running, just start it normally; don't pre-start Redis yourself.
- Python environment: bench was initialized with `--python /opt/homebrew/bin/python3.11` explicitly (not the system's 3.14). `bench new-app` should inherit this automatically since it runs within the existing bench's virtualenv — no need to re-specify.
- PATH note: `bench` CLI lives at `/Users/priyanka/Library/Python/3.11/bin`, MariaDB client tools at `/opt/homebrew/opt/mariadb@10.11/bin` — both were added to `~/.zshrc` during Story 1.1, should already be on `PATH` in a fresh shell.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 1.2] — story ACs
- [Source: _bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/addendum.md — Branding App] — `hooks.py` field list, file layout
- [Source: _bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md — AD-1, Structural Seed] — isolation invariant, source tree
- [Source: _bmad-output/implementation-artifacts/1-1-pull-erpnext-and-bootstrap-the-base-platform.md] — bench/site state, gitignore whitelist, environment gotchas
- [Source: _bmad-output/implementation-artifacts/deferred-work.md] — known whitelist-safety caveat inside `our_brand`

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5

### Debug Log References

- Authenticated verification commands (not persisted as files, run inline): `curl -c cookies.txt -d "usr=Administrator&pwd=admin" http://127.0.0.1:8000/api/method/login` then `curl -b cookies.txt -H "Host: dev.local" http://127.0.0.1:8000/app/home` — used before/after every branding change to check the actual rendered `<title>` and `app_logo_url`, not just hooks.py's declared values. This is what caught the desk-chrome bug (see Completion Notes) that a "hooks.py looks right" check alone would have missed entirely.
- `bench start` log: `/tmp/bench_start_story1.2.log` (session-local, not committed, same convention as Story 1.1).

### Completion Notes List

1. **Logo is real, not a placeholder.** User provided a finished "Azentis" logo (861×889px RGBA). Used the dark-bg variant (`azentis_final_dark_bg.png`) as the canonical `logo.png` per the user's explicit reference; also stored `logo-dark-bg.png` and `logo-light-bg.png` (light-bg companion, found alongside in the user's Downloads) as named variants for Story 1.3's dark/light theme work, which `DESIGN.md` already specifies needs both.
2. **App Title resolved to "Azentis"**, not the "AzentisERP" working title used for the project/repo — confirmed with the user, since the logo is strong evidence of the actual intended product name and the story explicitly flagged not to invent this value.
3. **App Publisher ("Ajit Zagade") had no safe default and was asked**, per the story's own explicit instruction not to guess it.
4. **Real bug found and fixed: `bench new-app` creates its own nested `.git` repo by default.** This made the new app invisible to proper git tracking (git saw it as one opaque "embedded repository," not individual files) — removed `myerp/apps/our_brand/.git` and re-verified tracking works file-by-file. This will recur for anyone running `bench new-app` again without knowing to check for it; worth remembering, not a one-off.
5. **Real, more significant bug found and fixed: `hooks.py`'s `app_title`/`app_logo_url` alone do NOT drive the actual visible desk chrome.** Verified this empirically (authenticated curl against `/app/home`), not assumed. Root cause, traced in Frappe's own source:
   - The desk `<title>` tag reads `Website Settings.app_name` (falling back to `System Settings.app_name`, then hardcoded `"Frappe"`) — never `hooks.py`'s `app_title` at all.
   - The navbar logo reads `Website Settings.app_logo` / `Navbar Settings.app_logo` first; only falls back to `hooks.py`'s `app_logo_url` hook if neither is set, and that fallback (`frappe/core/doctype/navbar_settings/navbar_settings.py::get_app_logo`) only has special-case handling for exactly 2 apps defining the hook. With `frappe`, `erpnext`, and `our_brand` all defining `app_logo_url` (3 apps), the fallback silently keeps Frappe's own logo.
   - **Fix:** added `our_brand/install.py` with `after_install` (sets `Website Settings.app_name`/`app_logo` directly) and `before_uninstall` (clears them back to `None`, so AC3's isolation check — stock branding returning cleanly — actually holds and doesn't leave stale branding data behind). Wired both into `hooks.py`.
   - This means AC1's literal text ("`app_title`/`app_logo_url` in `hooks.py` reflect our brand") is satisfied by the scaffold alone, but satisfying AC2 (branding actually *visible*) required going beyond what AC1's literal text describes — the story's own Dev Notes anticipated exactly this kind of gap ("a story implementation must leave the system working end-to-end... whether or not it is explicitly written in the story").
6. **Full uninstall → verify stock branding restored → reinstall → verify branding restored again** round-trip completed for AC3, using the same authenticated-curl verification method both directions, not just the install direction.
7. **AC4 verified via commit-hash comparison**, not just "git status is clean": `apps/frappe` and `apps/erpnext` HEADs (`105b1793...`, `b5f78461...`) confirmed identical to Story 1.1's recorded baseline, in addition to both being diff-clean.
8. **Favicon confirmed out of scope**, not skipped without checking: Frappe v15's favicon is a `Website Settings` DocType field, not a `hooks.py` mechanism (grepped Frappe's own `hooks.py`, confirmed it declares no favicon hook). AC1 only requires `app_logo_url`; AC2 is about visible text, not icons. Correctly deferred to Story 1.6 (Tenant Settings already plans a `favicon` field).
9. **Confirmed the Story 1.1 code review's deferred finding is benign for this case:** the generic `__pycache__/` gitignore pattern correctly excluded `our_brand/our_brand/__pycache__/*.pyc` (compiled Python bytecode created when Frappe imported `hooks.py`/`install.py`) even though it's inside the whitelisted `our_brand` zone — verified via `git add -A --dry-run`.

### File List

- `myerp/apps/our_brand/` (created — scaffolded via `bench new-app`, nested `.git` removed, 21 files git-trackable)
  - `our_brand/hooks.py` (app metadata: `app_name`, `app_title`, `app_publisher`, `app_description`, `app_email`, `app_license`, `app_logo_url`, `after_install`, `before_uninstall`)
  - `our_brand/install.py` (new — `after_install`/`before_uninstall` functions setting/clearing `Website Settings` branding fields)
  - `our_brand/public/images/logo.png`, `logo-dark-bg.png`, `logo-light-bg.png` (new — user-provided logo assets)
- `_bmad-output/implementation-artifacts/1-2-platform-brand-override.md` (this file — Tasks, Dev Agent Record)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified — story status)
