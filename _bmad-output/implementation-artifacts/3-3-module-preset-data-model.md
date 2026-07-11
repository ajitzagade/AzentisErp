---
baseline_commit: d281db7
---

# Story 3.3: Module Preset Data Model

Status: done

## Story

As the platform operator,
I want business-type presets stored as data,
so that adding a fifth preset later never requires a code change.

## Acceptance Criteria

1. Given the Module Preset DocType, when it's created, then it holds `preset_name` + an ordered `modules` list in the same Table MultiSelect shape as `enabled_modules` (AD-5).

## Dev Notes — Read Before Starting

**Reuse Story 3.1's `Tenant Enabled Module` child doctype — do not create a second one.** AD-5's "same Table MultiSelect shape as `enabled_modules`" literally means the same child-row shape (a `Link` to `Module Def`), not merely a visually similar one. `Tenant Enabled Module` already is exactly that shape and has no `Tenant Settings`-specific fields on it (just `module` → `Module Def`) — it's a generic "one row = one module reference" child doctype, equally valid as the `options` for `Module Preset.modules`. Creating a near-identical second child doctype (e.g. `Module Preset Module`) would be pure duplication with zero behavioral difference, violating this project's "create only what's needed" discipline.

**Not a Single DocType, unlike Tenant Settings.** `Module Preset` will have exactly 4 records (Story 3.4), so it's a normal multi-row DocType — `issingle` unset/0. `preset_name` is a plain `Data` field; use it as the autoname field (`autoname: "field:preset_name"`) so records are addressable by their own name (e.g. `"Retail"`, `"Services"`) rather than an auto-generated hash, matching the pattern `Tenant Settings`'s own docname convention doesn't need but a lookup-by-name doctype like this one benefits from.

**Scope boundary vs. Story 3.4**: this story is the DocType shape only — no seed data, no apply-to-tenant logic. Story 3.4 populates the 4 real preset records and builds the "apply to a tenant" action. Do not create any records or apply-logic here.

**AD-5's own text, for context** (already read during Epic 3's initial investigation): "Module Preset is its own DocType (name + ordered module list). Applying a preset at onboarding copies its module list into the new Tenant Settings record as a snapshot — not a live foreign key." The "snapshot, not live FK" behavior is Story 3.4's job (the actual copy operation) — this story just needs the ordered list to exist in a form that supports being copied cleanly (a `Table MultiSelect` field naturally copies as independent child rows when read and re-inserted elsewhere, which is exactly what "snapshot" means here — no special code needed at the schema level for that property, it falls out of how Frappe child tables work).

### Previous Story Intelligence (Story 3.1)

- `Tenant Enabled Module` child doctype (`istable: 1`, one `Link module → Module Def` field) already exists at `our_brand/our_brand/azentis/doctype/tenant_enabled_module/` — reference its exact shape, reuse its `name` as the `options` value.
- Doctype-folder gotcha still applies: new doctypes go in `our_brand/our_brand/azentis/doctype/<name>/`, not `our_brand/our_brand/doctype/<name>/` (Story 1.6's silent-failure bug).
- Verification method: `bench --site <name> migrate`, then console checks via `frappe.get_meta()`.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile; console-piped multi-line/conditional Python can silently misbehave (Story 3.2) — prefer single unconditional statements, verify state in a fresh console invocation.

## Tasks / Subtasks

- [x] Task 1: Create the `Module Preset` DocType (AC: 1)
  - [x] Created `our_brand/our_brand/azentis/doctype/module_preset/` (`__init__.py`, `module_preset.json`, `module_preset.py`)
  - [x] Fields: `preset_name` (`Data`, `reqd: 1`, `unique: 1`), `modules` (`Table MultiSelect`, `options: "Tenant Enabled Module"` — reused Story 3.1's child doctype, no duplicate created)
  - [x] `autoname: "field:preset_name"`
- [x] Task 2: Migrate and verify (AC: 1)
  - [x] `bench --site dev.local migrate` — succeeded, no errors
  - [x] Console: `frappe.get_meta("Module Preset").autoname` → `"field:preset_name"`; `modules` field → `fieldtype: "Table MultiSelect"`, `options: "Tenant Enabled Module"`
  - [x] Created a throwaway test record (`preset_name: "Test Preset"`, `modules: [CRM, Stock]`) — confirmed it inserted cleanly and read back with `stored_modules: ["CRM", "Stock"]`, order preserved; deleted afterward
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `bench --site dev.local migrate` → succeeded
- Console: `AUTONAME: field:preset_name`, `MODULES_FIELDTYPE: Table MultiSelect OPTIONS: Tenant Enabled Module`, test record created and read back with modules `['CRM', 'Stock']` in order
- Cleanup: test record deleted
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Reused Story 3.1's `Tenant Enabled Module` child doctype exactly as planned** — no second, near-identical child doctype created. AD-5's "same Table MultiSelect shape" requirement is satisfied literally, not just similarly.
- **Smallest story in Epic 3 so far** — a single DocType with two fields, no business logic. Consistent with the epic's own sequencing: this is pure schema, Story 3.4 is where the real seed data and apply-logic live.
- No automated test framework, consistent with every prior story's documented decision.

### File List

- `myerp/apps/our_brand/our_brand/azentis/doctype/module_preset/__init__.py` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/module_preset/module_preset.json` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/module_preset/module_preset.py` (new)
