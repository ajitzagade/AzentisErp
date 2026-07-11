---
baseline_commit: 12f1496
---

# Story 1.2: Platform Brand Override

Status: ready-for-dev

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

- [ ] Task 1: Scaffold the Branding App (AC: 1)
  - [ ] `bench new-app our_brand` — run from the bench root (`myerp/`, created in Story 1.1). Working name only per PRD §1 (final brand name unconfirmed) — use `our_brand` exactly, do not invent a different name.
  - [ ] Confirm the scaffold lands at `myerp/apps/our_brand/` — this is the one path under the bench that Story 1.1's `.gitignore` whitelist already tracks (`!myerp/apps/our_brand`). Verify with `git status`/`git add -A --dry-run` from the repo root that the new app's files are now staged as trackable (not gitignored) — this is the first real test of that whitelist pattern, deferred from Story 1.1's own review specifically for this moment.
- [ ] Task 2: Set app metadata in `hooks.py` (AC: 1)
  - [ ] Set `app_name = "our_brand"` (the internal Frappe app identifier — stays lowercase/snake_case regardless of the eventual public-facing brand name)
  - [ ] Set `app_title` to the public-facing product name (working title "AzentisERP" per PRD, unless the user specifies otherwise when this story runs — ask if unclear, do not silently invent a different name than what's used throughout planning)
  - [ ] Set `app_publisher` to the operator's name/company (ask the user for this value if not already established — it wasn't specified in planning and has no safe default to assume)
  - [ ] Set `app_description` (PRD suggests "Unified Business Management Platform" as a placeholder — confirm with user or use as-is)
  - [ ] Set `app_logo_url = "/assets/our_brand/images/logo.png"` pointing at a logo asset placed in Task 3
- [ ] Task 3: Add logo and favicon assets (AC: 1, 2)
  - [ ] Create `myerp/apps/our_brand/our_brand/public/images/` directory
  - [ ] Place a logo image at `logo.png` (or matching whatever `app_logo_url` in Task 2 points to) — ask the user for an actual logo file; if none is available yet, use a simple, clearly-placeholder image (do not fabricate a "real" logo design — that's a design decision outside this story's and this agent's scope) and flag it as a placeholder needing replacement in Completion Notes
  - [ ] Favicon: Frappe's favicon mechanism is normally set via `website_context` or a site-level `Website Settings` field, not purely `hooks.py` — confirm the correct v15 mechanism during implementation (check `frappe/frappe`'s own `hooks.py` for the pattern it uses) rather than assuming; this wasn't fully specified in planning
- [ ] Task 4: Install `our_brand` on the dev site and verify desk chrome (AC: 1, 2)
  - [ ] `bench --site dev.local install-app our_brand`
  - [ ] `bench start` (if not already running from Story 1.1), load the desk UI, confirm: browser tab title shows the new `app_title`, not "Frappe"/"ERPNext"; navbar/sidebar shows no visible "Frappe" or "ERPNext" string
  - [ ] Explicitly check the places Frappe's own branding tends to hide: browser tab favicon+title, the `/app` sidebar header, any "About" or system console page — do not assume checking one page is sufficient
- [ ] Task 5: Verify isolation — uninstall/reinstall round-trip (AC: 3, 4)
  - [ ] `bench --site dev.local uninstall-app our_brand` (or equivalent) — confirm stock Frappe/ERPNext branding returns cleanly, no leftover broken state
  - [ ] Reinstall `our_brand` afterward so the site is left in the intended branded state, not the uninstalled one
  - [ ] `git status`/`git diff` in `myerp/apps/frappe` and `myerp/apps/erpnext` — confirm still completely clean (matches Story 1.1's baseline: `frappe @ 105b1793`, `erpnext @ b5f78461`) — this is the concrete AC4 check, not just an assumption that nothing touched them

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

### Debug Log References

### Completion Notes List

### File List
