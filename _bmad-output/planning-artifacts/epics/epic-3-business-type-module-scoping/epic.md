---
epic: 3
title: Business-Type Module Scoping
status: approved
source: ../../epics.md
---

# Epic 3: Business-Type Module Scoping

Control exactly which ERP modules a tenant sees, with sensible default bundles (Retail/Services/Manufacturing/General) applied automatically, so SMB clients aren't overwhelmed by irrelevant modules.

**FRs covered:** FR9, FR10
**Architecture:** AD-4 (nav-level toggling, not RBAC), AD-5 (presets are data, snapshot-copied not live FK), AD-6 (warn-only dependency checks via one shared function)

## Story 3.1: Add Module Toggling to Tenant Settings

As the platform operator,
I want Tenant Settings to hold a per-tenant list of enabled modules,
So that module visibility becomes tenant-configurable data, not a code path.

**Acceptance Criteria:**

**Given** Tenant Settings (Story 1.5)
**When** the `enabled_modules` Table MultiSelect field is added
**Then** it references canonical Module Def names (AD-2's data-shape rule)

**Given** a tenant with no `enabled_modules` set yet (new tenant, empty)
**When** the sidebar renders
**Then** it fails open to showing all modules — never fails closed to showing none (consistent with Epic 1's fail-open convention)

## Story 3.2: Filter Sidebar by Enabled Modules

As a tenant's staff user,
I want to see only my business's relevant modules in the sidebar,
So that I'm not overwhelmed by ones I don't use.

**Acceptance Criteria:**

**Given** a tenant's `enabled_modules` excludes Manufacturing
**When** any user in that tenant views the sidebar
**Then** Manufacturing does not appear (FR9)

**Given** a module is disabled for a tenant
**When** a user navigates directly to that module's URL
**Then** access is NOT blocked — this is nav-level only, not a permission boundary (AD-4, explicit non-goal at MVP)

**Given** `enabled_modules` changes in Tenant Settings
**When** the sidebar next renders
**Then** it reflects the change without a restart (reuses Story 1.5's cached-accessor pattern)

## Story 3.3: Module Preset Data Model

As the platform operator,
I want business-type presets stored as data,
So that adding a fifth preset later never requires a code change.

**Acceptance Criteria:**

**Given** the Module Preset DocType
**When** it's created
**Then** it holds `preset_name` + an ordered `modules` list in the same Table MultiSelect shape as `enabled_modules` (AD-5)

## Story 3.4: Seed the Four Business-Type Presets

As the platform operator,
I want the four named presets (Retail, Services, Manufacturing, General) to actually exist as usable records,
So onboarding can apply one immediately — not just have an empty mechanism.

**Acceptance Criteria:**

**Given** the Module Preset DocType (Story 3.3)
**When** seed data runs
**Then** four records exist: **Retail** = Stock+POS+Accounts+CRM, **Services** = Projects+CRM+HR+Accounts, **Manufacturing** = Manufacturing+Stock+Purchasing+Accounts, **General** = all toggleable modules (per `addendum.md`'s table)

**Given** a preset is applied to a tenant
**When** the action runs
**Then** the preset's module list is copied into that tenant's `enabled_modules` as a snapshot — not a live reference back to the preset (AD-5) — so editing the preset later doesn't retroactively change already-onboarded tenants

## Story 3.5: Warn on Module Dependency Violations

As the platform operator,
I want to be warned (not blocked) if a module toggle would break a dependency,
So mistakes are visible without losing flexibility.

**Acceptance Criteria:**

**Given** a documented dependency map (e.g., Sales requires Accounting) and exactly one validation function (`our_brand.module_rules.validate_dependencies()`, AD-6)
**When** a preset is applied or a module is manually toggled
**Then** both flows call this same function — no duplicated logic

**Given** a toggle would disable a module another enabled module depends on
**When** it's applied
**Then** a warning is shown but the action is NOT blocked (PRD §10.6, warn-only decision)
