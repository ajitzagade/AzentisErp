# Story 1.1: Fork ERPNext and Bootstrap the Base Platform

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the platform operator,
I want our own fork of ERPNext running on a Frappe Bench,
so that we have a controlled, mergeable codebase to build every later customization on top of.

## Acceptance Criteria

1. Given GitHub org access, when ERPNext is forked under our org, then `github.com/OUR_ORG/erpnext` exists as our controlled copy, on the `version-15` branch. [Source: prd.md §10.7]
2. Given a bench initialized with stock Frappe Framework (`bench init --frappe-branch version-15`, from the official `frappe/frappe` — deliberately NOT forked), when `bench get-app erpnext` pulls from our fork's URL, then the bench's installed apps include our forked ERPNext, not a direct pull from the upstream `frappe/erpnext` repo. [Source: ARCHITECTURE-SPINE.md AD-1]
3. Given a new site on this bench, when `install-app erpnext` runs, then the setup wizard completes and all inherited ERPNext modules load (CRM, Sales, Purchasing, Accounting, HR, Inventory, Projects, Manufacturing, Assets, Support, Website, Workflows, Reports), with zero customization applied yet.
4. This story introduces no customization of its own — it is the unmodified inherited foundation every later story in Epic 1 brands on top of. This is the exact point from which AD-1's "core is never modified" becomes a checkable fact (verifiable via `git diff` against upstream in every later story, and directly tested in Epic 5 Story 5.5).

## Tasks / Subtasks

- [ ] Task 1: Fork ERPNext under the org's GitHub account (AC: 1)
  - [ ] Fork `https://github.com/frappe/erpnext` to `https://github.com/OUR_ORG/erpnext` — **`OUR_ORG` is a placeholder; the real GitHub org name was never specified in planning. Confirm with the user before running this step — do not guess.**
  - [ ] Ensure the `version-15` branch exists on the fork (mirrors upstream's `version-15`)
  - [ ] Add an `upstream` remote pointing at `https://github.com/frappe/erpnext.git` for future merges — not used by this story, but Epic 5 (Stories 5.4/5.5) needs it and it's free to set up now
- [ ] Task 2: Install prerequisites on the dev machine (AC: 2)
  - [ ] Python 3.11+, Node.js **20 or 22 LTS** (not 18 — see Dev Notes), MariaDB **10.11+** (not just 10.6 — see Dev Notes), Redis, wkhtmltopdf, yarn, git, pip
  - [ ] `pip install frappe-bench`
- [ ] Task 3: Initialize the bench with stock Frappe Framework (AC: 2)
  - [ ] `bench init <bench-name> --frappe-branch version-15` — pulls Frappe Framework from the official `frappe/frappe`, unforked
  - [ ] Verify Frappe Framework is not pointed at any custom fork URL — `apps/frappe`'s git remote must be the official repo
- [ ] Task 4: Pull the forked ERPNext into the bench (AC: 2)
  - [ ] `bench get-app erpnext --branch version-15 https://github.com/OUR_ORG/erpnext` (verify exact flag order against the installed `bench` CLI's own `--help` — minor syntax differences exist across bench versions)
  - [ ] Verify `apps/erpnext`'s git remote points to the fork, not `frappe/erpnext`
- [ ] Task 5: Create a site and install ERPNext (AC: 3)
  - [ ] `bench new-site <site-name>`
  - [ ] `bench --site <site-name> install-app erpnext`
  - [ ] `bench start`, complete the setup wizard in a browser
  - [ ] Confirm every inherited ERPNext module loads with no errors
- [ ] Task 6: Establish the zero-customization baseline (AC: 4)
  - [ ] `git status`/`git diff` in both `apps/frappe` and `apps/erpnext` — confirm no local modifications exist beyond what `bench` itself manages
  - [ ] Note the commit hashes of `apps/frappe` and `apps/erpnext` at this point — this is the baseline later stories (and Epic 5 Story 5.5's merge-isolation proof) diff against

## Dev Notes

- **This is the first story in the entire project.** No prior code, no prior stories, no git repository exists yet in the working directory. This story IS the foundation — every later story in every epic builds on what this one produces.
- Governed by Architecture Spine AD-1: dependency direction is one-way (`our_brand` → Frappe/ERPNext APIs, never reverse), and Frappe/ERPNext core is **never** modified for customization, ever, starting from this story onward.
- **Verified version pins** (from Architecture Spine Stack table, itself web-verified — not assumed from training data):
  - Frappe Framework: `version-15` branch, **stock/unforked** from official `frappe/frappe` — this is a deliberate decision (PRD §10.7), not an oversight. Do not fork Frappe Framework itself.
  - ERPNext: `version-15` branch, forked under the org.
  - Python 3.11+.
  - Node.js: Frappe v15's own documented floor is 18+, but **actually deploy on 20 or 22 LTS** — Node 18 has been end-of-life since April 2025. Following Frappe's stated minimum literally would put this on an unsupported runtime.
  - MariaDB: Frappe v15's floor is 10.3.x, but MariaDB 10.6 reached its own end-of-life in July 2026 — **use 10.11+** (current LTS), not just "whatever satisfies the stated minimum."
  - Redis: latest stable compatible with Frappe v15.
- **Frappe/ERPNext version-16 exists (GA) but is deliberately not used.** Staying on v15 avoids a combined Python 3.14 + Node 24 + framework jump that's excessive risk for a solo, 1-month build. Do not "helpfully" upgrade to v16 — this was an explicit architecture decision, not an oversight.
- **`OUR_ORG` is an unresolved placeholder** carried through from planning — the PRD and Architecture Spine both use it as a stand-in because the actual GitHub org name was never specified. This must be resolved with the user before Task 1 runs; do not invent or guess an org name.
- `<bench-name>` and `<site-name>` in Tasks 3/5 are lower-stakes placeholders (local dev naming, not a public/legal identifier like `OUR_ORG`) — use `docs/product.md`'s original suggestion if no preference is given: bench name `myerp`, site name `dev.local`.
- This story deliberately does nothing beyond forking, bootstrapping, and installing. No branding, no multi-tenancy, no Tenant Settings, no `our_brand` app. Those all start in Story 1.2 onward. Resist adding anything not in the ACs above — the DB/entity-creation discipline for this whole project is "create only what the current story needs."

### Project Structure Notes

- Standard Frappe Bench layout: bench root containing `apps/frappe` (stock) and `apps/erpnext` (the fork). Nothing custom yet.
- The `our_brand` app referenced throughout every later story does **not** exist after this story — it's scaffolded in Story 1.2, not here.
- No `our_brand`-related files, directories, or references should appear anywhere in this story's deliverable.

### Testing Standards

- No formal automated test framework exists yet for this project (Architecture Spine's Deferred section: formal test/QA strategy is explicitly deferred for the solo 1-month MVP). Verification for this story is manual/observational per the ACs above — the setup wizard completing and every module loading with no errors is the acceptance bar, not a written test suite.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 1.1] — story ACs
- [Source: _bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md §10.7] — fork-scope decision (ERPNext only, not Frappe Framework)
- [Source: _bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/addendum.md — Local Dev Setup] — original bench command sequence
- [Source: _bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md — AD-1] — customization isolation invariant
- [Source: _bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md — Stack] — verified version pins
- Web-verified 2026-07-10: Frappe v15 requires Python 3.11+, Node 18+ (deploy target 20/22 LTS), MariaDB 10.3.x minimum (deploy target 10.11+); `bench get-app`/`bench init` flag syntax confirmed current against `frappe/bench` documentation.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
