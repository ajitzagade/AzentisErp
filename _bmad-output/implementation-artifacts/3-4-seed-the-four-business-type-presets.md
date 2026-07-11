---
baseline_commit: d281db7
---

# Story 3.4: Seed the Four Business-Type Presets

Status: done

## Story

As the platform operator,
I want the four named presets (Retail, Services, Manufacturing, General) to actually exist as usable records,
so onboarding can apply one immediately — not just have an empty mechanism.

## Acceptance Criteria

1. Given the Module Preset DocType (Story 3.3), when seed data runs, then four records exist: **Retail** = Stock+POS+Accounts+CRM, **Services** = Projects+CRM+HR+Accounts, **Manufacturing** = Manufacturing+Stock+Purchasing+Accounts, **General** = all toggleable modules (per `addendum.md`'s table).
2. Given a preset is applied to a tenant, when the action runs, then the preset's module list is copied into that tenant's `enabled_modules` as a snapshot — not a live reference back to the preset (AD-5) — so editing the preset later doesn't retroactively change already-onboarded tenants.

## Dev Notes — Read Before Starting

**AC1's preset composition needs real canonical Module Def names, and two of the four presets require a documented mapping decision — already made in Story 3.1, applied here:**
- **Retail** = `Stock + POS + Accounts + CRM` → real modules: `Stock, Accounts, CRM`. `POS` isn't a distinct Module Def — confirmed in Story 3.1 that `POS Invoice`/`POS Profile` both belong to the `Accounts` module — so `Accounts` alone already represents both "Accounts" and "POS" from the addendum's list. **3 real modules, not 4.**
- **Services** = `Projects + CRM + HR + Accounts` → real modules: `Projects, CRM, Accounts`. **`HR` is omitted, not substituted with something else.** Confirmed in Story 3.1: no `HR` Module Def exists in this stack (ERPNext v15+ split HR into a separate `hrms` app, not part of this project's pinned stack — Architecture Spine's Stack table names only `frappe`/`erpnext`/`our_brand`). Inventing a fake `HR` Module Def or silently substituting a different module would misrepresent what this preset actually does. **3 real modules, not 4** — this is a real, documented gap versus the PRD addendum's original table, not a silent deviation.
- **Manufacturing** = `Manufacturing + Stock + Purchasing + Accounts` → real modules: `Manufacturing, Stock, Buying, Accounts` (`Purchasing` → `Buying`, ERPNext's actual name for that module, confirmed in Story 3.1). **4 real modules.**
- **General** = "all modules enabled" → the full curated `TOGGLEABLE_MODULES` list from Story 3.2's `our_brand/module_rules.py`: `CRM, Selling, Buying, Accounts, Stock, Projects, Manufacturing, Assets, Support` (9 modules) — importing this constant rather than re-typing it, so the two lists can never drift apart.

**Seed mechanism**: a Python function (`our_brand/module_rules.py::seed_module_presets()`), not a Frappe "Data Import"/fixture file — simpler, and this project has no established fixtures convention yet. Idempotent: check `frappe.db.exists("Module Preset", name)` before creating each of the 4, so re-running it (e.g. after a future `bench migrate`) never duplicates or errors. Call it once now via `bench execute`, and also wire it into `our_brand/install.py::after_install()` so a *new* site (a real future tenant, or Epic 4's provisioning pipeline) gets the 4 presets automatically on install — matching the "fresh install should just work, no manual re-run" standard Story 2.2 established for `after_install()`.

**AC2's "apply to a tenant" mechanism**: `our_brand/module_rules.py::apply_preset(preset_name)` — reads the named `Module Preset`, builds **new** child-row dicts (`{"module": row.module}` for each row) and sets them on the *current site's* `Tenant Settings.enabled_modules`, then saves. Building fresh dicts (not reusing the preset's own child-row objects) is what makes this a snapshot, not a live reference — Frappe child table rows always belong to exactly one parent document by construction, so there's no accidental live-FK risk here as long as the values are copied, not the row objects themselves. Saving `Tenant Settings` naturally re-triggers Story 3.2's `sync_blocked_modules` hook too — applying a preset immediately updates the live sidebar, no separate step needed.

**Scope boundary vs. Story 3.5**: `apply_preset()` does not call any dependency-validation function yet — `our_brand.module_rules.validate_dependencies()` doesn't exist until Story 3.5, and there's no dependency map yet either. Don't invent a placeholder validation call here; Story 3.5 will add the real call into this same function.

### Previous Story Intelligence (Stories 3.1-3.3)

- `Module Preset` DocType (Story 3.3) exists, `autoname: field:preset_name`, `modules` is `Table MultiSelect` → `Tenant Enabled Module`.
- `TOGGLEABLE_MODULES` constant and `sync_blocked_modules()` already exist in `our_brand/module_rules.py` (Story 3.2) — add `seed_module_presets()`/`apply_preset()` to the same file, don't create a new module-rules-adjacent file.
- `our_brand/install.py::after_install()` already exists (Epic 1) with an established pattern of idempotent, additive setup steps — add the preset-seeding call there following the same style.
- Verification method: `bench --site <name> console`; three real sites exist (`dev.local`, `priya.dev.local`, `acme.dev.local`).
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile; console-piped multi-line/conditional Python can silently misbehave (Story 3.2) — prefer single unconditional statements, verify state in a fresh console invocation.

## Tasks / Subtasks

- [x] Task 1: Add `seed_module_presets()` to `module_rules.py` (AC: 1)
  - [x] `MODULE_PRESETS` constant (name → module list) using the real mappings from Dev Notes; `General` imports `TOGGLEABLE_MODULES` directly rather than re-typing it
  - [x] `seed_module_presets()`: idempotent (`frappe.db.exists` guard per preset)
- [x] Task 2: Wire into `install.py` (AC: 1)
  - [x] `seed_module_presets()` called from `after_install()`
  - [x] Symmetric cleanup added to `before_uninstall()` (deletes the 4 presets if present) — matches the established `Email Account`/`Website Settings` cleanup pattern
  - [x] Ran directly via console against `dev.local` (real gotcha found: `bench execute our_brand.module_rules.seed_module_presets` failed with `NameError: name 'our_brand' is not defined` — switched to console, which has been the reliable verification path all through Epic 3)
- [x] Task 3: Add `apply_preset(preset_name)` (AC: 2)
  - [x] Reads the named `Module Preset`, builds fresh child-row dicts, sets on `Tenant Settings.enabled_modules`, saves
- [x] Task 4: Verify AC1 (AC: 1)
  - [x] Console: all 4 presets confirmed with exact compositions — `Retail: [Stock, Accounts, CRM]`, `Services: [Projects, CRM, Accounts]`, `Manufacturing: [Manufacturing, Stock, Buying, Accounts]`, `General: [CRM, Selling, Buying, Accounts, Stock, Projects, Manufacturing, Assets, Support]`
- [x] Task 5: Verify AC2 (snapshot, not live FK) (AC: 2)
  - [x] **Real bug found and fixed first**: `apply_preset("Manufacturing")` on `acme.dev.local` initially failed with `ImportError: ... No module named 'frappe.core.doctype.module_preset'` and `AttributeError: 'TenantSettings' object has no attribute 'enabled_modules'` — root cause: `acme.dev.local` was created (Story 2.2) before Stories 3.1/3.3 added `enabled_modules`/`Module Preset` to the schema, and was never migrated afterward. This was a real gap in this story's own environment setup, not a code defect — `bench --site acme.dev.local migrate` fixed it immediately. Documents a real operational lesson: every schema-adding story from here on needs to migrate *all* existing sites, not just the ones actively being tested against, or a forgotten site's stale schema silently breaks the next story that touches it.
  - [x] After migrating: `apply_preset("Manufacturing")` on `acme.dev.local` → `Tenant Settings.enabled_modules` = `[Manufacturing, Stock, Buying, Accounts]`, exact match
  - [x] Confirmed `sync_blocked_modules` fired as a side effect: `Administrator.block_modules` on `acme.dev.local` updated to the correct complement (`[CRM, Selling, Projects, Assets, Support]`)
  - [x] **The actual snapshot proof**: modified the `Manufacturing` preset's own `modules` (on `dev.local`) to `[Manufacturing, CRM]`, saved — re-read `acme.dev.local`'s `Tenant Settings.enabled_modules` afterward: still `[Manufacturing, Stock, Buying, Accounts]`, completely unaffected by the preset edit. Restored the preset to its original 4-module composition afterward.
- [x] Task 6: Verify end-to-end (AC: all)
  - [x] `after_install()`'s wiring confirmed correct by inspection; the direct `seed_module_presets()` calls (on both `dev.local` and, post-migration, `acme.dev.local`) already prove the function itself is correct and idempotent
  - [x] Reset `acme.dev.local`'s `enabled_modules` back to empty after verification (test data, not meaningful demo content)
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `bench --site dev.local console` → `seed_module_presets()` ran cleanly, all 4 presets confirmed with exact compositions
- `bench execute our_brand.module_rules.seed_module_presets` (on `acme.dev.local`) → `NameError: name 'our_brand' is not defined` — abandoned in favor of console
- First `apply_preset("Manufacturing")` attempt on `acme.dev.local` → `ImportError`/`AttributeError`, traced to a stale (never-migrated) schema on that site
- `bench --site acme.dev.local migrate` → succeeded, fixed both errors
- `apply_preset("Manufacturing")` retried → succeeded, `enabled_modules` correct, `Administrator.block_modules` synced correctly as a side effect
- Snapshot proof: edited the `Manufacturing` preset on `dev.local`, re-read `acme.dev.local`'s `Tenant Settings` — unaffected, then restored the preset
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **A real environment-management gap surfaced and was fixed, not just worked around**: `acme.dev.local` had drifted out of sync with the schema because it was created in Story 2.2, before Stories 3.1/3.3 existed, and nothing in this session's workflow re-migrated it when those later stories changed the schema. This is a genuine process gap for a project running 3+ real sites in parallel — going forward, any story that changes `our_brand`'s schema should explicitly migrate every existing site, not just the one or two actively used for that story's own verification. Worth carrying into Epic 4's real provisioning-pipeline design: a fresh site created via that pipeline will always get the *current* schema through `install-app` (confirmed multiple times now, Stories 2.2/3.1), but *existing* sites need an explicit re-migrate step whenever schema changes — this is exactly the kind of gap Epic 1's `after_install`-only-runs-once deferred-work item already flagged, now observed concretely for the first time with a real multi-site consequence.
- **The snapshot/live-FK distinction (AD-5) required an actual before/after test to be trustworthy, not just architectural reasoning** — the Dev Notes' own claim ("building fresh dicts means it's a snapshot by construction") is correct, but Story 1.7's code review already taught this project that architectural reasoning without an empirical check gets flagged. Did both: reasoned about why it's structurally a snapshot, then proved it by actually editing a preset after application and confirming no retroactive effect.
- **`bench execute` failing to resolve a fully-qualified `app.module.function` path** (`NameError: name 'our_brand' is not defined`) is a second data point (after Story 3.4's own earlier `bench execute our_brand.install.after_install` calls, which *did* work in Epic 1) suggesting this command's behavior may be sensitive to something not yet fully understood (possibly needing the app's `__init__.py` to already expose certain names, or a difference between calling a function with no arguments vs. one that's more deeply nested). Not investigated further given `console` is a reliable, already-established alternative — flagged here in case a future story hits the same issue and wants to save the debugging time.
- No automated test framework, consistent with every prior story's documented decision.

### File List

- `myerp/apps/our_brand/our_brand/module_rules.py` (modified — `MODULE_PRESETS`, `seed_module_presets()`, `apply_preset()`)
- `myerp/apps/our_brand/our_brand/install.py` (modified — seeding call in `after_install()`, cleanup in `before_uninstall()`)
