---
baseline_commit: ece3a97
---

# Story 1.6: Tenant Settings Data Model

Status: done

## Story

As the platform operator,
I want a per-site settings record for tenant branding,
so that a tenant's identity is stored as data, not hardcoded per install.

## Acceptance Criteria

1. Given `our_brand` is installed on a site, when it's set up, then a Tenant Settings Single DocType exists with fields: `tenant_name`, `site_name`, `custom_domain`, `logo`, `favicon`, `login_background`, `primary_color`, `secondary_color`, `email_sender_name`, `email_footer_text` (AD-2). `enabled_modules` is deliberately NOT added yet — that's Epic 3's concern.
2. Given Tenant Settings is saved, when any code reads it, then it goes through one accessor (`frappe.get_cached_doc`), never a scattered raw doc-get call (AD-2).

## Dev Notes — Read Before Starting

**This is a pure data-model story — no consumer wiring yet.** Story 1.7 is what actually reads these fields to drive live branding. This story's job is narrower: the DocType exists with the right shape, and the one sanctioned read path (the accessor) exists and is correct, even though nothing calls it yet within this story. Do not pre-wire Story 1.7's injection logic here — that's explicit scope creep the epics' own story split warns against ("create tables/entities only when needed").

**DocType location, per the architecture spine's own file-map** (`ARCHITECTURE-SPINE.md` §Consistency Conventions / FR-Component map: `FR-7–FR-8 Per-tenant config & dynamic branding → our_brand/doctype/tenant_settings`): `our_brand/our_brand/doctype/tenant_settings/`.

**Single DocType, not a regular one** — `issingle: 1` in the JSON. A Single DocType has exactly one implicit record (backed by Frappe's `tabSingles` key-value table), no explicit `.insert()` needed for AC1 to be satisfied — the DocType schema existing and being syncable via `bench migrate` is what AC1 actually asks for ("a Tenant Settings Single DocType exists with fields..."), not a populated record. Do not add seed/default data beyond Frappe's own field defaults; population is a later provisioning concern (Epic 4).

**Field types** (no ACs specify exact Frappe field types — apply sensible, standard choices, since this is undocumented in epics.md and needs an implementation decision):
- `tenant_name`, `custom_domain`, `email_sender_name`: Data
- `site_name`: Data — informational, not derived from `frappe.local.site` automatically in this story (no AC asks for that behavior; keep it a plain field, don't add logic beyond what's asked)
- `logo`, `favicon`, `login_background`: Attach Image (matches how `Website Settings.app_logo`/`splash_image` are already typed in Frappe core — consistent convention, checked via `website_settings.json` before choosing)
- `primary_color`, `secondary_color`: Color (Frappe's native Color fieldtype — gives a color picker in the UI; matches `DESIGN.md`'s hex-value tokens directly, no extra validation code needed since the fieldtype already constrains input)
- `email_footer_text`: Small Text

**The accessor (AD-2, AC2)**: a single function, `our_brand.utils.get_tenant_settings()`, wrapping `frappe.get_cached_doc("Tenant Settings")` — add it next to `contrast_text_color()` in the existing `our_brand/our_brand/utils.py` (Story 1.3's file), not a new module. AD-2's own text confirms this is safe to treat as "cached and always fresh" simultaneously: "Frappe invalidates this cache automatically on save... 'reads on every request' and 'cached' are the same behavior, not a contradiction." Nothing in this story calls the accessor yet (no consumer exists until Story 1.7) — its existence and correctness is what AC2 asks for.

### Previous Story Intelligence (1.1–1.5)

- `our_brand/our_brand/utils.py` already exists (`contrast_text_color()` from Story 1.3) — add to it, don't create a second utils module.
- Verification method for a new DocType: `bench --site dev.local migrate` (syncs the DocType into the DB), then `bench --site dev.local console` to confirm `frappe.get_meta("Tenant Settings")` has exactly the expected fields and `frappe.get_cached_doc("Tenant Settings")` returns a valid doc.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile; `bench build --app our_brand` needed for any new JS/CSS (not relevant to this story — no client assets), but `bench migrate` is the relevant sync step for a new DocType, not `bench build`.

## Tasks / Subtasks

- [x] Task 1: Check `Website Settings`' field types for the Attach Image convention (AC: 1)
  - [x] Confirmed `app_logo`/`splash_image` are `"fieldtype": "Attach Image"` in `website_settings.json` — used the same type for `logo`/`favicon`/`login_background`
- [x] Task 2: Create the Tenant Settings DocType (AC: 1)
  - [x] Created `tenant_settings.json`/`tenant_settings.py`/`__init__.py` — `issingle: 1`, module `Azentis`, the 10 named fields (Data/Attach Image/Color/Small Text as decided in Dev Notes), no `enabled_modules` field
  - [x] **Real bug found and fixed**: initially placed the doctype folder at `our_brand/our_brand/doctype/tenant_settings/` — `bench migrate` completed with no errors, but `frappe.db.get_value("DocType", "Tenant Settings", ...)` returned `None` (the DocType silently never got created), and a later console call trying to load its controller threw `ImportError: No module named 'frappe.core.doctype.tenant_settings'`. Root cause: Frappe's doctype sync expects doctypes to live inside the *module's own* folder (`get_module_path("Azentis")` resolves to `our_brand/our_brand/azentis/`, matching `modules.txt`'s "Azentis" entry), i.e. `our_brand/our_brand/azentis/doctype/tenant_settings/`, not directly under the app's top-level `doctype/`. Moved the whole folder there (plus a `doctype/__init__.py` inside the module folder) and re-ran `bench migrate` — fixed, doctype now syncs correctly.
  - [x] `bench --site dev.local migrate` — succeeded after the path fix
- [x] Task 3: Add the accessor (AC: 2)
  - [x] Added `get_tenant_settings()` to the existing `our_brand/our_brand/utils.py` (next to `contrast_text_color()`), wrapping `frappe.get_cached_doc("Tenant Settings")`
- [x] Task 4: Verify (AC: all)
  - [x] Via `bench --site dev.local console`: `frappe.get_meta("Tenant Settings")` → `issingle: 1`, field list is exactly the 10 named fields (Section Break fields excluded from the check as expected, they're layout-only), `enabled_modules` confirmed absent
  - [x] `get_tenant_settings()` returns a valid doc: `doctype="Tenant Settings"`, `name="Tenant Settings"` (Single DocType's implicit name)
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- First `bench --site dev.local migrate` → completed with no visible errors, but doctype was NOT actually created (silent failure due to wrong folder location)
- `frappe.db.get_value("DocType", "Tenant Settings", ["module", "app"])` → `None`, revealing the silent failure
- Console attempt to load `TenantSettings` controller → `ImportError: No module named 'frappe.core.doctype.tenant_settings'`
- `frappe.get_module_path("Azentis")` → `.../our_brand/our_brand/azentis`, confirming the correct location
- Second `bench --site dev.local migrate` (after moving the folder) → succeeded, `our_brand` doctypes updated
- Console verification: `ISSINGLE: 1`, `FIELDS: [tenant_name, site_name, custom_domain, logo, favicon, login_background, primary_color, secondary_color, email_sender_name, email_footer_text]`, `HAS_ENABLED_MODULES: False`, `ACCESSOR_DOCTYPE: Tenant Settings`, `ACCESSOR_NAME: Tenant Settings`
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **The migrate-silently-succeeds-but-does-nothing failure mode is worth flagging for future stories**: `bench migrate` gave zero indication anything was wrong — no error, no warning, just a doctype that never appeared in the DB. This is the kind of gap real verification (querying the DB directly, not just checking the command's exit status) is meant to catch, consistent with the empirical-verification discipline established across Stories 1.1–1.5. A less careful pass would have marked this story done on the strength of "migrate ran without error."
- **Module-folder convention now documented for future doctype work**: any new `our_brand` DocType must live at `our_brand/our_brand/azentis/doctype/<doctype_name>/`, not `our_brand/our_brand/doctype/<doctype_name>/` — the module name (`Azentis`, from `modules.txt`) determines the folder Frappe actually scans. Relevant for Story 3.3 (Module Preset DocType) later in the roadmap.
- This story deliberately does not wire any consumer of `get_tenant_settings()` — confirmed no other story-1.1–1.5 file references it, keeping the scope boundary clean for Story 1.7 to be the first real consumer.
- No automated test framework, consistent with prior stories' documented decision — verification is console/DB-query-based.

### File List

- `myerp/apps/our_brand/our_brand/azentis/doctype/__init__.py` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_settings/__init__.py` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_settings/tenant_settings.json` (new)
- `myerp/apps/our_brand/our_brand/azentis/doctype/tenant_settings/tenant_settings.py` (new)
- `myerp/apps/our_brand/our_brand/utils.py` (modified — `get_tenant_settings()`)
