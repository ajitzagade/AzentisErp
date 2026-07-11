---
baseline_commit: d281db7
---

# Story 3.1: Add Module Toggling to Tenant Settings

Status: done

## Story

As the platform operator,
I want Tenant Settings to hold a per-tenant list of enabled modules,
so that module visibility becomes tenant-configurable data, not a code path.

## Acceptance Criteria

1. Given Tenant Settings (Story 1.6), when the `enabled_modules` Table MultiSelect field is added, then it references canonical Module Def names (AD-2's data-shape rule).
2. Given a tenant with no `enabled_modules` set yet (new tenant, empty), when the sidebar renders, then it fails open to showing all modules — never fails closed to showing none (consistent with Epic 1's fail-open convention).

## Dev Notes — Read Before Starting

**"Canonical Module Def names" are real ERPNext/Frappe data, verified against the actual bench, not invented.** Queried `Module Def` directly: real records are `erpnext`'s `Accounts, Assets, Bulk Transaction, Buying, Communication, CRM, EDI, ERPNext Integrations, Maintenance, Manufacturing, Portal, Projects, Quality Management, Regional, Selling, Setup, Stock, Subcontracting, Support, Telephony, Utilities`, plus `frappe`'s system-level modules (`Core, Custom, Desk, Email, Workflow, Automation, Printing, Social, Geo, Integrations, Contacts, Website`), plus `our_brand`'s own `Azentis` (not a business module, excluded from anything tenant-toggleable). `enabled_modules` must Link to real `Module Def` records via a proper `Table MultiSelect` child doctype, not free text.

**AC1's "Table MultiSelect" fieldtype, correct shape confirmed from a real example** (not `Block Module`, which is fieldtype `Table` with a free-text `Data` field, not an actual MultiSelect): read `Assignment Rule User` (ERPNext core) as the reference — a `Table MultiSelect` child doctype is `istable: 1` with exactly one `Link` field (`options` pointing at the target doctype) plus whatever else. Create a new child doctype, `Tenant Enabled Module`, with a single `Link` field `module` → `Module Def`. Add `enabled_modules` to `tenant_settings.json` as `fieldtype: "Table MultiSelect"`, `options: "Tenant Enabled Module"`.

**Real gap found and must be documented, not silently worked around: this project's ERPNext installation has no HR module.** ERPNext v15+ split HR/Payroll out into a separate `hrms` app (confirmed: no "HR" `Module Def` exists; the only HR-adjacent doctype, `Employee`, belongs to the generic `Setup` module, not a dedicated HR module). This project's Architecture Spine Stack table names only `frappe`/`erpnext`/`our_brand` — no `hrms`. This matters for Story 3.4 (the addendum's "Services: Projects + CRM + HR + Accounts" preset), not this story, but the underlying fact belongs here since it affects which Module Def names are even valid to reference. Do not invent a fake "HR" Module Def to paper over this — Story 3.4 will document the real preset composition without it.

**Curated "toggleable business modules" list, for later stories' reference (not enforced as a field-level restriction here)**: Story 3.4's presets and any future "General = all modules" definition should use this curated set — `CRM`, `Selling`, `Buying`, `Accounts`, `Stock`, `Projects`, `Manufacturing`, `Assets`, `Support` (9 real modules covering the addendum's Module Catalog's business-relevant categories; POS folds into `Accounts` since `POS Invoice`/`POS Profile` both belong to that module, confirmed via `frappe.db.get_value("DocType", "POS Invoice", "module")`). Frappe's own system-level modules (`Core`, `Custom`, `Desk`, etc.) and ERPNext's niche/setup ones (`Bulk Transaction`, `EDI`, `Regional`, `Setup`, `Telephony`, `Utilities`, etc.) are deliberately excluded — they aren't business-facing sidebar sections an SMB tenant would think of as a toggleable "module." This story's `enabled_modules` field itself is NOT restricted to only these 9 (an admin can technically Link any real Module Def) — the curation matters for Story 3.4's presets and Story 3.2's practical usage, not as a hard constraint on the field.

**AC2's fail-open mechanism, decided now for Story 3.2 to implement**: investigated Frappe's actual sidebar-filtering mechanism (`frappe/desk/desktop.py::get_workspace_sidebar_items()`) — it already filters out any Workspace whose `module` is in `frappe.get_cached_doc("User", frappe.session.user).get_blocked_modules()` (reads `User.block_modules`, a real, existing Frappe feature — not something to build from scratch). The natural fail-open implementation (Story 3.2's job, not this story's): when `Tenant Settings.enabled_modules` is empty, compute an empty block list (block nothing → show everything); when non-empty, block = curated list minus enabled. This story only needs to add the field — do not implement the sync logic here, that's explicitly Story 3.2's AC.

**Scope boundary**: this story adds exactly one field (plus its child doctype). No sidebar-filtering logic, no sync-to-User logic, no presets — those are Stories 3.2/3.3/3.4. Adding them here would violate the "create only what's needed now" discipline every prior epic has followed.

### Previous Story Intelligence (Epic 1, Epic 2)

- `tenant_settings.json`/`tenant_settings.py` live at `our_brand/our_brand/azentis/doctype/tenant_settings/` (Story 1.6 — note the real gotcha from that story: doctypes MUST live inside the app's *module* folder, `our_brand/our_brand/azentis/doctype/`, not `our_brand/our_brand/doctype/` — `bench migrate` silently no-ops on the wrong path with no error).
- New child doctypes follow the same module-folder rule: `our_brand/our_brand/azentis/doctype/tenant_enabled_module/`.
- Verification method: `bench --site <name> migrate` to sync, then `bench --site <name> console` to confirm field shape via `frappe.get_meta()`.
- Two real tenant sites exist for testing: `priya.dev.local`, `acme.dev.local` (plus the platform's own `dev.local`) — migrate all three, or at minimum `dev.local` and one tenant site, to confirm the new field/doctype syncs cleanly across sites.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Create the `Tenant Enabled Module` child doctype (AC: 1)
  - [x] Created `our_brand/our_brand/azentis/doctype/tenant_enabled_module/` (`__init__.py`, `tenant_enabled_module.json` — `istable: 1`, one `Link` field `module` → `Module Def`, `tenant_enabled_module.py`)
- [x] Task 2: Add `enabled_modules` to Tenant Settings (AC: 1)
  - [x] Added `modules_section` (Section Break) + `enabled_modules` (`Table MultiSelect`, `options: "Tenant Enabled Module"`) to `tenant_settings.json`
- [x] Task 3: Migrate and verify (AC: all)
  - [x] `bench --site dev.local migrate` — succeeded, no errors
  - [x] `bench --site priya.dev.local migrate` — succeeded, confirms the new doctype/field syncs cleanly on a second real site too, not just the platform's own
  - [x] Console: `frappe.get_meta("Tenant Settings").get_field("enabled_modules")` → `fieldtype: "Table MultiSelect"`, `options: "Tenant Enabled Module"`; child doctype's `module` field → `fieldtype: "Link"`, `options: "Module Def"`
  - [x] Fresh `Tenant Settings.enabled_modules` with no rows reads back as `[]`, not an error — confirms the exact fail-open data shape Story 3.2 will build on
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- Console query of real `Module Def` records confirmed the canonical name list documented in Dev Notes
- `frappe.db.get_value("DocType", "POS Invoice", "module")` → `"Accounts"`, confirming POS folds into Accounts, no separate module
- `frappe.db.exists("Module Def", "HR")` → `None`; `Employee` doctype's module → `"Setup"` — confirmed no dedicated HR module exists in this stack
- `bench --site dev.local migrate` / `bench --site priya.dev.local migrate` → both succeeded
- Console: field-shape and empty-list checks all passed as expected

### Completion Notes List

- **Investigated Frappe's real Table MultiSelect shape from a working example (`Assignment Rule User`) rather than guessing** — avoided repeating Story 1.6's "wrong folder location" class of mistake by checking a concrete precedent (`istable: 1` + one `Link` field) instead of assuming from the fieldtype's name alone. Also confirmed `Block Module` (superficially similar, already used by Frappe core for per-user module blocking) is deliberately *not* a Table MultiSelect — it uses a free-text `Data` field, not a `Link` — so it was not a safe template to copy from directly, only useful as a pointer to the *mechanism* (see next note).
- **Found Frappe's existing, real sidebar-filtering mechanism during this story's investigation, ahead of Story 3.2 needing it**: `frappe/desk/desktop.py::get_workspace_sidebar_items()` already filters out any Workspace whose `module` is in `User.get_blocked_modules()` (a real, existing Frappe feature, not something to build). This means Story 3.2 doesn't need to override or monkey-patch Frappe's sidebar code at all — it can sync `User.block_modules` from `Tenant Settings.enabled_modules` and get the filtering for free. Documented in Dev Notes for Story 3.2 to use directly rather than re-discovering.
- **Real, load-bearing gap found and documented rather than papered over**: this project's ERPNext installation has no HR module (split into a separate `hrms` app in ERPNext v15+, not part of this project's pinned stack). This directly affects Story 3.4's "Services: Projects + CRM + HR + Accounts" preset from the PRD addendum — flagged now so Story 3.4 doesn't silently invent a fake Module Def or get surprised later.
- No automated test framework, consistent with every prior story's documented decision.

### File List

- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_enabled_module/__init__.py` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_enabled_module/tenant_enabled_module.json` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_enabled_module/tenant_enabled_module.py` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_settings/tenant_settings.json` (modified — `enabled_modules` field)
