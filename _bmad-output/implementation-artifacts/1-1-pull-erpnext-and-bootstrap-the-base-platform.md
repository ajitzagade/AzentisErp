# Story 1.1: Pull ERPNext and Bootstrap the Base Platform

Status: ready-for-dev

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

- [ ] Task 1: Install prerequisites on the dev machine (AC: 1)
  - [ ] Python 3.11+, Node.js **20 or 22 LTS** (not 18 — see Dev Notes), MariaDB **10.11+** (not just 10.6 — see Dev Notes), Redis, wkhtmltopdf, yarn, git, pip
  - [ ] `pip install frappe-bench`
- [ ] Task 2: Initialize the bench with stock Frappe Framework (AC: 1)
  - [ ] `bench init <bench-name> --frappe-branch version-15` — pulls Frappe Framework from the official `frappe/frappe`, unforked. Use `myerp` if no preference is given (see Dev Notes).
  - [ ] Verify Frappe Framework is not pointed at any custom fork URL — `apps/frappe`'s git remote must be the official repo
- [ ] Task 3: Pull ERPNext directly from upstream, pinned (AC: 1)
  - [ ] `bench get-app erpnext --branch version-15 https://github.com/frappe/erpnext` (verify exact flag order against the installed `bench` CLI's own `--help` — minor syntax differences exist across bench versions)
  - [ ] Verify `apps/erpnext`'s git remote points directly at `frappe/erpnext` — no fork, no intermediate remote
  - [ ] Record the exact commit hash `apps/erpnext` resolves to at this point — this is the pin. Later "updates" (Epic 5, Stories 5.4/5.5) mean checking out a *newer* commit here, tested on staging first, never an untracked "whatever upstream has now"
- [ ] Task 4: Create a site and install ERPNext (AC: 2)
  - [ ] `bench new-site <site-name>` — use `dev.local` if no preference is given (see Dev Notes)
  - [ ] `bench --site <site-name> install-app erpnext`
  - [ ] `bench start`, complete the setup wizard in a browser
  - [ ] Confirm every inherited ERPNext module loads with no errors
- [ ] Task 5: Configure `ajitzagade/AzentisErp` to track only our own code (AC: 3)
  - [ ] Add `apps/frappe/` and `apps/erpnext/` to `.gitignore` in the `AzentisErp` repo — same treatment already given to the BMad tooling installation
  - [ ] Also gitignore bench-generated machine/site-local content that shouldn't be committed: `env/` (Python virtualenv), `sites/*/private/`, `sites/*/public/files/`, `logs/`, `config/pids/`
  - [ ] `apps/our_brand/` (doesn't exist yet — created in Story 1.2) is the one path under the bench that *will* be tracked once it exists
- [ ] Task 6: Establish the zero-modification baseline (AC: 4)
  - [ ] `git status`/`git diff` in both `apps/frappe` and `apps/erpnext` — confirm no local modifications exist beyond what `bench` itself manages
  - [ ] This baseline (the pinned commit hashes from Task 3, plus zero local diffs) is what Epic 5 Story 5.5 later re-verifies after a real upstream re-pin

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

### Debug Log References

### Completion Notes List

### File List
