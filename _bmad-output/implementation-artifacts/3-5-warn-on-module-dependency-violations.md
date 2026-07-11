---
baseline_commit: d281db7
---

# Story 3.5: Warn on Module Dependency Violations

Status: done

## Story

As the platform operator,
I want to be warned (not blocked) if a module toggle would break a dependency,
so mistakes are visible without losing flexibility.

## Acceptance Criteria

1. Given a documented dependency map (e.g., Sales requires Accounting) and exactly one validation function (`our_brand.module_rules.validate_dependencies()`, AD-6), when a preset is applied or a module is manually toggled, then both flows call this same function — no duplicated logic.
2. Given a toggle would disable a module another enabled module depends on, when it's applied, then a warning is shown but the action is NOT blocked (PRD §10.6, warn-only decision).

## Dev Notes — Read Before Starting

**AC1's "one seam, no duplicated logic" is best satisfied by `Tenant Settings.validate()`, not by calling `validate_dependencies()` separately from `apply_preset()` and some other manual-toggle hook.** Both the "preset applied" flow (Story 3.4's `apply_preset()`) and the "module manually toggled" flow (an admin editing `Tenant Settings.enabled_modules` directly in the desk UI) end the same way: a `Tenant Settings.save()` call. Frappe's document lifecycle runs a doctype controller's `validate()` method on *every* save, regardless of what triggered it — wiring `validate_dependencies()` into `TenantSettings.validate()` means there is exactly one call site in the codebase, and both flows reach it automatically without either one needing to remember to call it explicitly. This is a stronger reading of AD-6 ("enforced at one seam") than the original assumption (calling the function from two separate places) — decided during this story's own investigation, not assumed going in.

**Dependency map, initial and deliberately conservative** — only real, defensible functional relationships in ERPNext, not an exhaustive invented graph:
- `Selling` requires `Accounts` — the addendum's own explicit example ("Sales needs Accounting"): a Sales Invoice is fundamentally an accounting document.
- `Buying` requires `Accounts` — same reasoning, Purchase Invoice.
- `Manufacturing` requires `Stock` — BOMs and Work Orders operate on Stock items; manufacturing without inventory tracking doesn't function.

`CRM`, `Projects`, `Assets`, `Support` have no declared dependencies in this initial map — not because they have none in a broader business sense, but because inventing additional dependencies beyond what's clearly justified would violate this project's "don't add speculative logic" discipline. The map is data (a plain dict), not code — extending it later (per AD-5's own framing for presets, and AD-6's "one dependency map") is a data change, not a re-architecture.

**Warning mechanism**: `frappe.msgprint(text, indicator="orange", title="Module Dependency Warning")` for each violation found. `msgprint` without `raise_exception=True` never blocks the save — this is the built-in Frappe primitive for exactly PRD §10.6's "warn, don't block" requirement, not something to build from scratch.

**`validate_dependencies(enabled_modules)` is a pure function** (list of module names in → list of warning strings out), independently testable and independently callable — `TenantSettings.validate()` is a thin wrapper that calls it and `msgprint`s the results. This separation is what makes "exactly one validation function" (AC1's literal wording) meaningfully true — the *logic* lives in one pure function, not scattered across a controller method with side effects baked in.

**Real gotcha from Story 3.4, carried forward and already fixed for this story**: every existing site (`dev.local`, `priya.dev.local`, `acme.dev.local`) was re-migrated at the end of Story 3.4 after a drift was discovered — no new migration is expected to be needed for this story (no schema change, just a new Python function and a controller method), but confirm this assumption rather than skip verification on more than one site.

### Previous Story Intelligence (Stories 3.1-3.4)

- `our_brand/module_rules.py` already has `TOGGLEABLE_MODULES`, `sync_blocked_modules()`, `MODULE_PRESETS`, `seed_module_presets()`, `apply_preset()` — add `MODULE_DEPENDENCIES`/`validate_dependencies()` to the same file.
- `TenantSettings` controller (`tenant_settings.py`) is currently a bare `class TenantSettings(Document): pass` — this story is what finally gives it real behavior.
- Verification method: `bench --site <name> console`, single unconditional statements (multi-line/conditional blocks piped via stdin have repeatedly misbehaved in Epic 3 — Stories 3.2/3.4).
- Three real sites: `dev.local`, `priya.dev.local`, `acme.dev.local` — all freshly migrated as of Story 3.4's fix.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Add `MODULE_DEPENDENCIES`/`validate_dependencies()` to `module_rules.py` (AC: 1, 2)
  - [x] `MODULE_DEPENDENCIES = {"Selling": ["Accounts"], "Buying": ["Accounts"], "Manufacturing": ["Stock"]}`
  - [x] `validate_dependencies(enabled_modules)`: pure function, returns warning strings for any enabled module whose dependency isn't also enabled
- [x] Task 2: Wire into `TenantSettings.validate()` (AC: 1)
  - [x] `tenant_settings.py`: `validate()` calls `validate_dependencies()`, `frappe.msgprint()` per warning (`indicator="orange"`, no `raise_exception` — non-blocking)
- [x] Task 3: Verify AC1 (one seam, both flows) (AC: 1)
  - [x] Confirmed `apply_preset()` reaches `validate()` automatically via its own `.save()` call — no code change needed in `apply_preset()` itself, and no explicit second call site anywhere; verified by observing `apply_preset("Retail")` correctly producing zero warnings (proving `validate()` did run during that save, just found nothing to warn about for that particular preset)
  - [x] Confirmed a manual `enabled_modules` edit + `save()` reaches the same `validate()` — same code path, directly observed via `frappe.message_log` after each manual save in Task 4
- [x] Task 4: Verify AC2 (warn, don't block) (AC: 2)
  - [x] Set `enabled_modules` to `[Manufacturing]` only on `acme.dev.local` — save succeeded (`SAVE_SUCCEEDED`, record actually persisted), `frappe.message_log` contained exactly `[{'message': 'Manufacturing is enabled but requires Stock, which is not enabled.', 'title': 'Module Dependency Warning', 'indicator': 'orange'}]`
  - [x] Set `enabled_modules` to `[Manufacturing, Stock]` (compliant) — save succeeded, `message_log` empty
  - [x] `apply_preset("Retail")` → `message_log` empty, `enabled_modules` correctly `[Stock, Accounts, CRM]` — confirms a real preset doesn't trigger warnings against itself (Retail has no `Selling`, so its `Selling→Accounts` dependency never applies)
- [x] Task 5: Verify end-to-end (AC: all)
  - [x] Reset `acme.dev.local`'s `enabled_modules` back to empty after verification
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- Console (`acme.dev.local`): `enabled_modules=[Manufacturing]` → save succeeded, `message_log` = `[{'message': 'Manufacturing is enabled but requires Stock, which is not enabled.', ...}]`
- Console: `enabled_modules=[Manufacturing, Stock]` → save succeeded, `message_log` = `[]`
- Console: `apply_preset("Retail")` → `message_log` = `[]`, `enabled_modules` = `['Stock', 'Accounts', 'CRM']`
- Reset: `enabled_modules` cleared back to `[]`
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Found a stronger design for AD-6's "one seam" during investigation, not assumed from the start**: the story's own initial framing (before investigation) anticipated calling `validate_dependencies()` explicitly from both `apply_preset()` and some manual-toggle-specific hook — two call sites. Realized during Dev Notes analysis that Frappe's own document lifecycle already provides a single, unconditional seam (`Document.validate()`, which runs on *every* save regardless of caller) — wiring the check there means `apply_preset()` needed zero changes at all, and there is exactly one place in the entire codebase that calls `validate_dependencies()`. This is a stronger, more literal satisfaction of "one seam, no duplicated logic" than the originally-assumed design.
- **`validate_dependencies()` kept as a pure function, separate from the `msgprint` side effect** — deliberately, so "exactly one validation function" (AC1's literal wording) refers to real, testable logic (list in, list of warnings out), not a controller method entangled with UI side effects. `TenantSettings.validate()` is a thin two-line wrapper around it.
- **Verification scope decision**: unlike Story 3.2 (which needed live-dev-server curl testing because the claim was specifically about what a running desk session's sidebar API returns), this story's mechanism (`Document.save() → validate()`) is exercised identically whether triggered via console or a real desk-UI save — there's no live-server-specific behavior being tested here. Console-based verification (`frappe.message_log` inspection after real `.save()` calls) is sufficient and was not supplemented with a redundant curl-based pass.
- **Dependency map deliberately conservative** (3 entries, all with a clear real-world basis) rather than an exhaustive invented graph across all 9 toggleable modules — consistent with this project's "don't add speculative logic" discipline throughout. Documented as data, easily extended later without a code change.
- No automated test framework, consistent with every prior story's documented decision. This is the last story in Epic 3.

### File List

- `myerp/apps/our_brand/our_brand/module_rules.py` (modified — `MODULE_DEPENDENCIES`, `validate_dependencies()`)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_settings/tenant_settings.py` (modified — `validate()`)

## Review Findings (2026-07-12)

Consolidated code review covering all of Epic 3 (Stories 3.1-3.5). Three parallel reviewers (Blind Hunter, Edge Case Hunter, Acceptance Auditor) ran against a correctly-constructed diff (learning from Epic 1/2's earlier diff-construction mistakes — untracked files included from the start) plus direct access to the real bench. See `deferred-work.md`'s "Deferred from: code review of Epic 3" entry for the full deferred list.

**Patches applied (6, all in `module_rules.py`/`tenant_settings.py`/`hooks.py`/new `patches/` file):**

1. **[HIGH, confirmed by two independent reviewers with real reproduction] `sync_blocked_modules()`'s write was silently discarded for any user with a Frappe "Module Profile" assigned.** `User.validate() → validate_allowed_modules()` unconditionally re-derives `block_modules` from the linked Module Profile on every `User.save()` — including the very save `sync_blocked_modules()` itself issues — overwriting our value immediately after we set it. Reproduced empirically: created a Module Profile blocking `Stock`, assigned it to a test user, ran the sync — the user's `block_modules` reverted to the profile's own list, silently defeating the tenant's `enabled_modules` choice for that one user. Fixed by excluding users with a `module_profile` set from the sync loop (`module_profile: ["in", ["", None]]` filter) — Frappe's own Module Profile mechanism is already authoritative for those users, and there is no way to override a core `validate()` hook without touching Frappe source (forbidden, AD-1). Re-verified after the fix: a user with a Module Profile keeps their profile's own `block_modules` untouched; a user without one still syncs correctly against `enabled_modules`.
2. **`apply_preset()` was never callable by anything except a `bench console` session** — no `@frappe.whitelist()`, no API route, no client script. AC2 says "when the action runs," implying a real, usable action; as originally merged there wasn't one. Fixed: `@frappe.whitelist()` added, with a `System Manager`-only authorization check (it mutates tenant-wide config and cascades into a write on every System User). Verified via real authenticated HTTP call: `POST /api/method/our_brand.module_rules.apply_preset` with `preset_name=Retail` → `200`, `Tenant Settings.enabled_modules` correctly updated; the same call as a non-System-Manager user → `403 PermissionError`; an unknown preset name → clean `417 ValidationError: Unknown module preset: ...` (previously a raw, unguarded `DoesNotExistError` traceback).
3. **`MODULE_PRESETS["General"] = TOGGLEABLE_MODULES` aliased the same list object rather than copying it** — any future in-place mutation of the "General" preset's module list would have silently corrupted the shared `TOGGLEABLE_MODULES` constant `sync_blocked_modules()` depends on globally. Fixed: `list(TOGGLEABLE_MODULES)`.
4. **`seed_module_presets()` could raise an unhandled `DuplicateEntryError`** if two callers raced between the `exists()` check and the `insert()` call. Fixed: `insert()` wrapped in `try/except frappe.DuplicateEntryError: pass`.
5. **Existing sites never received new/changed presets except by someone remembering to manually re-run `seed_module_presets()`** — Story 3.4's own Completion Notes already documented discovering and hand-fixing exactly this drift on `acme.dev.local`. Root-caused and fixed properly this time: added a `post_model_sync` Frappe patch (`our_brand/patches/seed_module_presets.py`) that runs `seed_module_presets()` on every `bench migrate`, not just fresh installs. Verified live: `priya.dev.local` (which had never been manually seeded) received all 4 presets automatically on its next migrate, with zero manual intervention.
6. **AD-2's architecture text inaccurately claimed sidebar filtering "goes through the cached Tenant Settings accessor."** Story 3.2's actual, and better, design syncs `enabled_modules` into `User.block_modules` at Tenant Settings save time rather than re-reading Tenant Settings on every desk-sidebar request — a real, deliberate architectural choice that was never reconciled back into AD-2's own written rule. Corrected AD-2 to describe the actual mechanism and explain why it's a legitimate exception, not a violation.

All patches verified against the real running bench (`priya.dev.local`/`acme.dev.local`), including real authenticated HTTP calls for the whitelisting/authorization fixes, not just console-based checks.

**Deferred (non-blocking, logged to `deferred-work.md`)**: no sync hook for newly-created/promoted Users (sidebar stays unfiltered until the next unrelated Tenant Settings save), no reset-to-fail-open hook if Tenant Settings itself is deleted, synchronous/non-transactional per-user sync loop (fine at SMB scale), unintended `clear_notifications()`/`create_contact` job side effects from reusing full `User.save()` as the sync mechanism, `enabled_modules` not constrained to the curated module set at the validate level, no row-locking against concurrent preset-apply/manual-toggle races, force-deleted `Module Def` leaving dangling references, only 1 of 4 presets' "no self-triggered warnings" claim empirically verified (the other 3 checked by replaying the logic, not by a live `apply_preset()` call), and a plausible but undecided `Assets → Accounts` dependency-map addition.
