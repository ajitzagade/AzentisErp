---
baseline_commit: d281db7
---

# Story 3.2: Filter Sidebar by Enabled Modules

Status: done

## Story

As a tenant's staff user,
I want to see only my business's relevant modules in the sidebar,
so that I'm not overwhelmed by ones I don't use.

## Acceptance Criteria

1. Given a tenant's `enabled_modules` excludes Manufacturing, when any user in that tenant views the sidebar, then Manufacturing does not appear (FR9).
2. Given a module is disabled for a tenant, when a user navigates directly to that module's URL, then access is NOT blocked — this is nav-level only, not a permission boundary (AD-4, explicit non-goal at MVP).
3. Given `enabled_modules` changes in Tenant Settings, when the sidebar next renders, then it reflects the change without a restart (reuses Story 1.6's cached-accessor pattern).

## Dev Notes — Read Before Starting

**Reuse Frappe's own existing sidebar-filtering mechanism — do not build a new one.** Confirmed during Story 3.1's investigation: `frappe/desk/desktop.py::get_workspace_sidebar_items()` already filters out any Workspace whose `module` is in `frappe.get_cached_doc("User", frappe.session.user).get_blocked_modules()` (reads `User.block_modules`, a real Table field, `options: "Block Module"`). Grepped every call site of `get_blocked_modules()`/`block_modules` in Frappe core (`frappe/config/__init__.py`, `frappe/desk/desktop.py`, `frappe/desk/doctype/desktop_icon/desktop_icon.py`) — all three are nav/UI-level (sidebar list, desktop icons, module config), **none touch Role Permissions or route/API access**, confirming this mechanism already *is* AD-4's "navigation-level, not a security boundary" behavior by construction — AC2 doesn't need anything built, it's automatically true because `block_modules` was never wired into permission checks anywhere in Frappe core. This story's actual job is: sync `User.block_modules` from `Tenant Settings.enabled_modules`, nothing more.

**Sync mechanism**: a `doc_events` hook on `Tenant Settings`, `on_update`, calling `our_brand.module_rules.sync_blocked_modules()`. Logic:
- If `enabled_modules` is empty → clear every user's `block_modules` (block nothing → show everything) — this is AC's fail-open case, inherited directly from Story 3.1 AC2.
- If non-empty → for every user, set `block_modules` to (curated toggleable module list, from Story 3.1's Dev Notes: `CRM, Selling, Buying, Accounts, Stock, Projects, Manufacturing, Assets, Support`) minus whatever is in `enabled_modules`.
- Apply to every `enabled=1, user_type="System User"` User on the site (skip Guest/disabled accounts — irrelevant to desk sidebar rendering). Since `Tenant Settings` is one record per site (a Single), "every user on this tenant" is simply "every user on this site" — no additional scoping needed, Frappe's own DB-per-site isolation (Epic 2) already guarantees this only ever touches the current site's users.
- Synchronous, not a background job — SMB tenant scale (tens of users, not thousands) doesn't need async here; matches this project's "don't over-engineer" discipline.

**New file: `our_brand/module_rules.py`** — houses the curated `TOGGLEABLE_MODULES` list constant and `sync_blocked_modules()`. Deliberately the same file AD-6 already names for Story 3.5's `validate_dependencies()` function — creating it now with just what this story needs, Story 3.5 adds to it later, avoiding a second module-list constant existing in two places.

**AC3's "no restart" is automatic, not something to implement**: `get_workspace_sidebar_items()` reads `frappe.get_cached_doc("User", ...)` fresh on every request (Frappe's own per-request desk boot), and this story's `on_update` hook updates the real `User` doc the moment `Tenant Settings` is saved — the very next page load already reflects it. No caching layer of our own to invalidate, unlike `get_tenant_settings()`'s own cache (which Story 1.6/AD-2 already handle automatically on save).

**Why not read `Tenant Settings.enabled_modules` directly inside a sidebar-rendering hook instead of syncing to `User.block_modules`?** Considered and rejected: Frappe's `get_workspace_sidebar_items()` is a whitelisted, un-hookable function (no `before_request`/filter hook point exists for it specifically), and overriding it entirely would mean re-implementing its full permission/domain-filtering logic ourselves — a much larger, riskier surface than syncing one existing field Frappe already designed for exactly this purpose. Syncing to `User.block_modules` is the lower-risk, "reuse what exists" choice, consistent with this project's approach throughout Epic 1/2 (e.g. Story 1.3's CSS-injection-over-template-replacement decision).

### Previous Story Intelligence (Story 3.1)

- `Tenant Settings.enabled_modules` (Table MultiSelect → `Tenant Enabled Module` → `Module Def`) already exists and syncs cleanly on `dev.local`/`priya.dev.local`.
- Curated module list already decided in Story 3.1: `CRM, Selling, Buying, Accounts, Stock, Projects, Manufacturing, Assets, Support`.
- Verification method: `bench --site <name> console` to set `enabled_modules`, trigger save, then inspect real `User.block_modules` rows; curl/authenticated desk check for the actual sidebar content is the strongest possible verification (matches Epic 1's "verify what actually renders" discipline) — use `frappe.client.get_list`/direct API call to `frappe.desk.desktop.get_workspace_sidebar_items` with a real session cookie, not just DB inspection.
- Three real sites exist: `dev.local`, `priya.dev.local`, `acme.dev.local`.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Create `our_brand/module_rules.py` (AC: 1, 3)
  - [x] `TOGGLEABLE_MODULES = ["CRM", "Selling", "Buying", "Accounts", "Stock", "Projects", "Manufacturing", "Assets", "Support"]`
  - [x] `sync_blocked_modules(doc, method=None)`: reads `doc.enabled_modules`, computes the blocked set (empty enabled → empty blocked, fail-open), iterates `enabled=1, user_type="System User"` Users, sets `block_modules`, saves each
- [x] Task 2: Wire the hook (AC: 3)
  - [x] Added `doc_events = {"Tenant Settings": {"on_update": "our_brand.module_rules.sync_blocked_modules"}}` to `hooks.py`
- [x] Task 3: Verify AC1 (Manufacturing excluded) end-to-end (AC: 1)
  - [x] **Real bug in initial test design found and corrected**: first tried verifying against `Administrator` — `block_modules` synced correctly (`Administrator.block_modules` included `Manufacturing`), but the live sidebar API still showed Manufacturing. Root cause: `get_workspace_sidebar_items()`'s own code has `has_access = "Workspace Manager" in frappe.get_roles()`, and if `has_access` is true, `filters = []` — a full bypass of blocked-modules filtering. Administrator implicitly has every role, so this test case was fundamentally unable to observe the filtering at all, regardless of whether the sync logic was correct. Fixed by creating a real non-admin test user (`staff@priya.test`, `Sales User` role) on `priya.dev.local` and re-testing against them — this is the only way to actually exercise this AC's real-world scenario (a regular tenant staff member, not the platform's own super-user).
  - [x] Set `priya.dev.local`'s `enabled_modules` to `[CRM, Accounts, Stock]`, confirmed `staff@priya.test`'s `block_modules` synced to `[Selling, Buying, Projects, Manufacturing, Assets, Support]`
  - [x] Authenticated as `staff@priya.test`, called the real running dev server's `frappe.desk.desktop.get_workspace_sidebar_items` — returned modules: `Accounts, Automation, CRM, Core, Integrations, Quality Management, Setup, Stock, Website` — **Manufacturing confirmed absent**, CRM/Accounts/Stock (the enabled ones) confirmed present
- [x] Task 4: Verify AC2 (nav-level only, not a permission boundary) (AC: 2)
  - [x] **Test design corrected again**: first attempt called `frappe.client.get_list` on `BOM` with the `Sales User` role alone — got a `403 PermissionError`, but that was an ordinary Frappe *role*-permission rejection (Sales User has no BOM access at all, unrelated to module blocking), not evidence either way for this AC. Added `Manufacturing User` role to the same test user (confirmed `block_modules` was unaffected by the role change — still blocked Manufacturing) and retried
  - [x] With a role that *does* grant BOM access, the same user (Manufacturing still hidden from their sidebar) successfully called `frappe.client.get_list?doctype=BOM` → `200 {"message":[]}`, not a `PermissionError` — definitively confirms module-blocking never restricts direct API/DocType access, only sidebar visibility
- [x] Task 5: Verify AC3 (no restart) (AC: 3)
  - [x] All of Task 3/4's verification happened live against the already-running `bench start` dev server with zero restarts between the `hooks.py` change, the `Tenant Settings` saves, and the curl checks — confirms both the new hook registration and each subsequent state change took effect immediately
  - [x] Cleared `enabled_modules` back to `[]` — confirmed `block_modules` cleared to `[]` too, and the live sidebar API immediately showed Manufacturing again (`MANUFACTURING_PRESENT_NOW: True`) — fail-open reversion confirmed live, no restart
- [x] Task 6: Verify end-to-end (AC: all)
  - [x] Deleted the test user (`staff@priya.test`) after verification
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- First AC1 test (Administrator) → sync correct but sidebar unchanged, traced to `get_workspace_sidebar_items()`'s `has_access` bypass for users with the effective "Workspace Manager" role (Administrator always does)
- Created `staff@priya.test` (Sales User role) — first two creation attempts silently failed (weak-password validation error aborted the console-piped script mid-way); succeeded on the third attempt with a strong password, verified in a fresh console session
- `curl` as `staff@priya.test` → sidebar correctly excludes Manufacturing when not in `enabled_modules`
- First AC2 test (`BOM` access, Sales User only) → `403`, traced to ordinary role-permission rejection, not module-blocking — added `Manufacturing User` role, retried → `200 {"message":[]}`, confirming module-blocking never restricts direct access
- Fail-open reversion (`enabled_modules` cleared) → `block_modules` cleared, live sidebar immediately showed Manufacturing again
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Two of this story's own verification attempts were initially flawed and had to be corrected before they proved anything** — both caught by actually reasoning about the result rather than accepting the first response. The Administrator test would have given false confidence ("sync ran, sidebar unchanged, so... it doesn't work?") without realizing Administrator is specifically exempted from this filtering by Frappe's own code; the Sales-User-only BOM test would have given a false negative for AC2 ("blocked!") that was actually just an unrelated role-permission rejection. Both are recorded in detail above since they're exactly the kind of "verification claim doesn't test what it claims to test" gap this project's code reviews have repeatedly flagged in earlier epics — catching them here, in the same pass, rather than in a later review.
- **Zero new sidebar-filtering logic was written** — the entire mechanism is Frappe's own pre-existing `User.block_modules` + `get_workspace_sidebar_items()`/`desktop_icon.py` filtering, confirmed via Story 3.1's investigation to already be nav-level-only by construction (never touches Role Permissions). This story's only code is the sync function keeping `block_modules` up to date with `Tenant Settings.enabled_modules`.
- **Console-via-stdin flakiness with multi-line/conditional Python blocks, again** — same class of issue noted implicitly in earlier stories' `for`-loop problems; confirmed here that an `if`-guarded block's body can silently fail to execute when piped into IPython, and that a mid-script exception can abort a later `frappe.db.commit()` without obviously failing the whole script. Worked around by using single, unconditional statements and verifying state in a fresh console invocation rather than trusting a single script's own printed output.
- No automated test framework, consistent with every prior story's documented decision.

### File List

- `myerp/apps/our_brand/our_brand/module_rules.py` (new — `TOGGLEABLE_MODULES`, `sync_blocked_modules()`)
- `myerp/apps/our_brand/our_brand/hooks.py` (modified — `doc_events`)
