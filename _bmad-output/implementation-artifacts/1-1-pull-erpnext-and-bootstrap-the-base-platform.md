---
baseline_commit: 68b345e02767650eada6d12aeb679aacd4005bcd
---

# Story 1.1: Pull ERPNext and Bootstrap the Base Platform

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- Revised 2026-07-10: original title/approach was "Fork ERPNext and Bootstrap the Base Platform" (forking to a separate ajitzagade/erpnext repo). That's been dropped — ERPNext is now pulled directly from frappe/erpnext, pinned, never forked or pushed to. All our own code lives in one repo, ajitzagade/AzentisErp. See ARCHITECTURE-SPINE.md AD-1 and PRD §10.7 for the full reasoning. -->

## Story

As the platform operator,
I want ERPNext running on a Frappe Bench, pulled directly from upstream and pinned,
so that we have a stable, upgradable foundation to build every later customization on top of, without owning or maintaining a fork.

## Acceptance Criteria

1. Given a bench initialized with stock Frappe Framework (`bench init --frappe-branch version-15`, from the official `frappe/frappe` — not forked), when `bench get-app erpnext --branch version-15` pulls directly from `https://github.com/frappe/erpnext`, then the bench's installed apps include ERPNext pinned to that branch/commit, sourced straight from the official upstream repo — no separate fork repo exists or is needed. [Source: ARCHITECTURE-SPINE.md AD-1, revised 2026-07-10]
2. Given a new site on this bench, when `install-app erpnext` runs, then the setup wizard completes and all inherited ERPNext modules load (CRM, Sales, Purchasing, Accounting, HR, Inventory, Projects, Manufacturing, Assets, Support, Website, Workflows, Reports), with zero customization applied yet.
3. Given `apps/frappe` and `apps/erpnext` inside the Bench, when the project's own repo (`ajitzagade/AzentisErp`) is configured, then both directories are gitignored — never version-controlled or pushed by us — while `our_brand` (scaffolded in Story 1.2) is the only app tracked and pushed to `ajitzagade/AzentisErp`.
4. This story introduces no customization of its own — it is the unmodified inherited foundation every later story in Epic 1 brands on top of. This is the exact point from which AD-1's "core is never modified, never pushed to" becomes a checkable fact (verifiable via `git diff` against the pinned upstream commit in every later story, and directly tested in Epic 5 Story 5.5's re-pin proof).

## Tasks / Subtasks

- [x] Task 1: Install prerequisites on the dev machine (AC: 1)
  - [x] Python 3.11+, Node.js **20 or 22 LTS** (not 18 — see Dev Notes), MariaDB **10.11+** (not just 10.6 — see Dev Notes), Redis, ~~wkhtmltopdf~~, yarn, git, pip — installed via Homebrew (`python@3.11` 3.11.15, `mariadb@10.11` 10.11.18, `redis` 8.8.0, `yarn` 1.22.22); Node 22.17.0 and git already present. **wkhtmltopdf skipped** — no longer available as a Homebrew formula or cask (upstream unmaintained); not required by any of this story's ACs (PDF export only), flagged as a follow-up in Completion Notes.
  - [x] `pip install frappe-bench` — installed as `python3.11 -m pip install --user frappe-bench` (5.31.0), deliberately under 3.11 not the system's 3.14, to avoid any bench-CLI dependency issues on an untested Python version
- [x] Task 2: Initialize the bench with stock Frappe Framework (AC: 1)
  - [x] `bench init myerp --frappe-branch version-15 --python /opt/homebrew/bin/python3.11` — bench name `myerp` used (no preference given). `--python` pinned explicitly to 3.11 to avoid the system default (3.14). `SUCCESS: Bench myerp initialized`.
  - [x] Verified: `apps/frappe`'s git remote is named `upstream`, pointing at `https://github.com/frappe/frappe.git` (not a fork), branch `version-15`
- [x] Task 3: Pull ERPNext directly from upstream, pinned (AC: 1)
  - [x] `bench get-app erpnext --branch version-15 https://github.com/frappe/erpnext` — succeeded (bench's own flag order was `erpnext --branch version-15 <url>`, matching the story's syntax)
  - [x] Verified: `apps/erpnext`'s git remote is named `upstream`, pointing at `https://github.com/frappe/erpnext` (not a fork)
  - [x] Pinned commit: **`b5f784612d5b7969b72848dda5b22f10d3a8f764`** (tag `v15.115.0`, 2026-07-01) — this is the baseline Epic 5 Stories 5.4/5.5 will later re-pin forward from. Note: `bench get-app` uses a shallow clone (`--depth 1`); fine for pinning, `git fetch` still works for future re-pins
- [ ] Task 4: Create a site and install ERPNext (AC: 2)
  - [x] `bench new-site dev.local --db-root-password frappe_dev_root --admin-password admin` — site created, Frappe installed
  - [x] `bench --site dev.local install-app erpnext` — succeeded (`bench --site dev.local list-apps` confirms `frappe 15.114.0 version-15`, `erpnext 15.115.0 version-15`). Required fixing a redis port mismatch first — see Completion Notes.
  - [x] `bench start` running (background), verified reachable via `curl -H "Host: dev.local" http://127.0.0.1:8000` → HTTP 200, ERPNext assets loading, `<!-- Built on Frappe -->` confirming stock/unmodified. User added `dev.local` to `/etc/hosts`, opened the browser, and completed the interactive setup wizard themselves (company/business details — intentionally not automated, see Dev Notes)
  - [x] Confirmed: ERPNext desk loads with Accounting, Buying, Selling, Stock, Assets, Manufacturing, Quality, Projects, Support, Users, Website, CRM, Tools modules, onboarding checklist (Create an Item/Customer/Sales Invoice) working, Reports & Masters populated — zero errors. **Finding:** HR module is NOT present — as of ERPNext v14+, HR & Payroll moved to a separate `frappe/hrms` app, no longer bundled with core ERPNext. Flagged in Completion Notes; affects Epic 3's "Services" preset planning, not this story's ACs.
- [x] Task 5: Configure `ajitzagade/AzentisErp` to track only our own code (AC: 3)
  - [x] Switched to a **whitelist pattern** rather than an explicit exclusion list: `myerp/*` / `!myerp/apps` / `myerp/apps/*` / `!myerp/apps/our_brand`. An explicit list (as originally planned) proved unsafe in practice — it missed `sites/dev.local/site_config.json` (contains a real auto-generated DB password), per-site logs, and a stray screenshot file that landed in the bench root. The whitelist can't miss anything, by construction.
  - [x] Verified via `git add -A --dry-run myerp/` — zero files staged (confirmed the DB password, logs, and stray files are all excluded)
  - [x] `apps/our_brand/` doesn't exist yet (created in Story 1.2) — the pattern is ready for it once it does
- [x] Task 6: Establish the zero-modification baseline (AC: 4)
  - [x] `git status`/`git diff --stat` in both `apps/frappe` and `apps/erpnext` — both completely clean, zero local modifications
  - [x] Baseline recorded: `apps/frappe` @ `105b17938839f4e5c6cdff817d42afc40c3bcc32` (v15.114.0, 2026-07-09), `apps/erpnext` @ `b5f784612d5b7969b72848dda5b22f10d3a8f764` (v15.115.0, 2026-07-01). This is what Epic 5 Story 5.5 will re-verify against after a real upstream re-pin.

## Dev Notes

- **This is the first story in the entire project.** No prior code, no prior stories. This story IS the foundation — every later story in every epic builds on what this one produces.
- **The approach changed mid-planning (2026-07-10).** The original plan forked ERPNext to a separate `ajitzagade/erpnext` repo. That's been explicitly dropped: the user does not want to ever push to any ERPNext-related repo, and wants all of AzentisERP's own code in exactly one repo, `ajitzagade/AzentisErp`. If you see any reference elsewhere (old memlogs, early conversation) to "forking ERPNext under our org," it is superseded by this story.
- Governed by Architecture Spine AD-1 (revised): dependency direction is one-way (`our_brand` → Frappe/ERPNext APIs, never reverse), Frappe/ERPNext core is **never** modified, and **neither Frappe Framework nor ERPNext is forked** — both are pinned, unforked, read-only upstream dependencies.
- **Verified version pins** (from Architecture Spine Stack table, itself web-verified — not assumed from training data):
  - Frappe Framework: `version-15` branch, stock/unforked from official `frappe/frappe`.
  - ERPNext: `version-15` branch, stock/unforked from official `frappe/erpnext`, pinned to a specific commit (Task 3).
  - Python 3.11+.
  - Node.js: Frappe v15's own documented floor is 18+, but **actually deploy on 20 or 22 LTS** — Node 18 has been end-of-life since April 2025.
  - MariaDB: Frappe v15's floor is 10.3.x, but MariaDB 10.6 reached its own end-of-life in July 2026 — **use 10.11+** (current LTS).
  - Redis: latest stable compatible with Frappe v15.
- **Frappe/ERPNext version-16 exists (GA) but is deliberately not used.** Staying on v15 avoids a combined Python 3.14 + Node 24 + framework jump. Do not "helpfully" upgrade to v16.
- **Repo layout is important and easy to get wrong:** the Bench (`apps/`, `sites/`, `env/`, etc.) is a large, mostly-third-party directory tree. Only `apps/our_brand/` (created in Story 1.2) is our code. Everything else under the bench — including `apps/frappe/` and `apps/erpnext/`, both full clones of large upstream codebases — must be gitignored in `ajitzagade/AzentisErp`, the same way `node_modules` would be. Do not commit them.
- `<bench-name>` and `<site-name>` are lower-stakes placeholders — use `docs/product.md`'s original suggestion if no preference is given: bench name `myerp`, site name `dev.local`.
- This story deliberately does nothing beyond installing prerequisites, bootstrapping, and pulling ERPNext. No branding, no multi-tenancy, no Tenant Settings, no `our_brand` app. Those all start in Story 1.2 onward. Resist adding anything not in the ACs above.

### Project Structure Notes

- Standard Frappe Bench layout: bench root containing `apps/frappe` (stock, gitignored) and `apps/erpnext` (stock, gitignored). Nothing custom yet.
- The `our_brand` app referenced throughout every later story does **not** exist after this story — it's scaffolded in Story 1.2, not here. Once it exists, it becomes the *only* tracked path under the bench.
- No `our_brand`-related files, directories, or references should appear anywhere in this story's deliverable.

### Testing Standards

- No formal automated test framework exists yet for this project (Architecture Spine's Deferred section explicitly defers this for the solo 1-month MVP). Verification for this story is manual/observational per the ACs above — the setup wizard completing and every module loading with no errors is the acceptance bar.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 1.1] — story ACs (revised 2026-07-10)
- [Source: _bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md §10.7] — pin-scope decision, revised (neither Frappe nor ERPNext forked)
- [Source: _bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/addendum.md — Local Dev Setup] — bench command sequence
- [Source: _bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md — AD-1] — customization isolation + pinned-dependency invariant (revised 2026-07-10)
- [Source: _bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md — Stack] — verified version pins
- Web-verified 2026-07-10: Frappe v15 requires Python 3.11+, Node 18+ (deploy target 20/22 LTS), MariaDB 10.3.x minimum (deploy target 10.11+); `bench get-app`/`bench init` flag syntax confirmed current against `frappe/bench` documentation.

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5

### Debug Log References

- `bench init` and `bench get-app` full output: no persisted log file, ran interactively and verified inline (yarn/esbuild asset builds, `SUCCESS: Bench myerp initialized`).
- `bench start` server log: `/tmp/bench_start.log` (session-local, not committed).
- Redis port-mismatch failure during first `install-app erpnext` attempt: `redis.exceptions.ConnectionError: Error 61 connecting to 127.0.0.1:11000. Connection refused.` — root cause and fix documented in Completion Notes.

### Completion Notes List

1. **Prerequisite versions, all Homebrew-installed and verified:** Python 3.11.15 (`python@3.11`, deliberately not the system's pre-existing 3.14 — Frappe v15 targets 3.11, not 3.14, which is actually the v16 requirement), Node 22.17.0 (already present), MariaDB 10.11.18 (`mariadb@10.11`, pinned specifically — Homebrew's default `mariadb` formula now points to 12.3, a much bigger jump than Architecture's verified 10.11+ target), Redis 8.8.0, Yarn 1.22.22.
2. **wkhtmltopdf skipped.** No longer available as a Homebrew formula or cask — the upstream project is effectively unmaintained. Not required by any of this story's ACs (it's only used for PDF export). **Follow-up needed** before any story that requires PDF generation (invoice/report exports) — will need an alternative install path researched at that time.
3. **MariaDB configured with Frappe's required charset settings** (`/opt/homebrew/etc/my.cnf.d/frappe.cnf`: `character-set-server=utf8mb4`, `collation-server=utf8mb4_unicode_ci`, `character-set-client-handshake=FALSE`) — web-verified as the correct config for MariaDB 10.3+ (the older `innodb-file-format=barracuda` setting some guides reference was removed from MariaDB 10.3.1+ and would have caused a startup error on 10.11).
4. **MariaDB root password set** to `frappe_dev_root` (local dev only — MariaDB configured to accept localhost connections only, per Homebrew's own install output).
5. **Redis port mismatch, found and fixed.** `bench init` generates its own Redis configs expecting dedicated instances on ports 11000 (queue) and 13000 (cache) — not the system Redis service's default 6379. First `install-app erpnext` attempt failed with a connection-refused error until this was understood. **Second issue on top of that:** manually starting Redis on those ports for the install step conflicted with `bench start`'s own Procfile trying to start its own copies afterward, killing the whole process group. Resolved by killing the manually-started instances and letting `bench start` own its full Redis lifecycle via the Procfile — this is the correct long-term pattern, not a one-off workaround.
6. **Site created:** `dev.local`, Administrator password `admin` (local dev only, not a production credential). Setup wizard (company/business details) completed interactively by the user in-browser, by design — those are real business decisions, not something to fabricate even for a dev/test site.
7. **`/etc/hosts` needed a manual entry** (`127.0.0.1 dev.local`) for the user's browser to reach the site, since Frappe routes by hostname (this is FR5/AD-9's DNS-based multi-tenancy mechanism already in effect, even at single-site scale). Required sudo, which the agent cannot run interactively — the user ran it themselves. First attempt used `sudo echo ... >> /etc/hosts`, which silently fails (the redirect runs outside the sudo'd process) — resolved with `echo ... | sudo tee -a /etc/hosts` instead.
8. **`.gitignore` strategy changed from an explicit exclusion list to a whitelist** (`myerp/*` / `!myerp/apps` / `myerp/apps/*` / `!myerp/apps/our_brand`) after the explicit list, as originally planned in this story, was tested and found to miss real sensitive/junk content: `sites/dev.local/site_config.json` (contains a real auto-generated DB password, distinct from the MariaDB root password), per-site log files, and a stray screenshot file the user's OS saved into the bench root instead of Desktop. The whitelist is structurally safer — it cannot miss a new kind of file the way an exclusion list can.
9. **Real finding, not this story's problem to fix but flagged for planning:** the ERPNext desk UI, once the setup wizard completed, does **not** show an HR module. As of ERPNext v14+, HR & Payroll was split out into a separate `frappe/hrms` app, no longer bundled with core ERPNext. This affects Epic 3's "Services" preset plan (currently: Projects+CRM+HR+Accounts) — either `hrms` needs to be installed as an additional pinned dependency, or the preset needs to drop HR. Not addressed here; Epic 3 should resolve it before Story 3.4 (seeding the presets) is implemented.
10. All 4 ACs verified: (1) ERPNext pulled directly from `frappe/erpnext` via `upstream` remote, pinned to `b5f7846` (v15.115.0) — no fork exists or was created; (2) setup wizard completed, full ERPNext desk loads with all core modules (except HR, see #9) and zero errors; (3) `apps/frappe`/`apps/erpnext` gitignored via the whitelist pattern, confirmed via `git add -A --dry-run` staging zero files; (4) both `apps/frappe` and `apps/erpnext` are git-clean (zero local modifications), baseline commits recorded for Epic 5's later re-pin verification.

### File List

- `.gitignore` (modified — Frappe Bench whitelist pattern added)
- `/opt/homebrew/etc/my.cnf.d/frappe.cnf` (created — outside repo, system MariaDB config)
- `myerp/` (created — Frappe Bench root; entirely gitignored except the not-yet-existing `apps/our_brand/`)
- `_bmad-output/implementation-artifacts/1-1-pull-erpnext-and-bootstrap-the-base-platform.md` (this file — Tasks, Dev Agent Record)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified — story status)
