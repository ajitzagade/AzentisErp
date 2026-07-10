---
stepsCompleted: [1, 2, 3]
inputDocuments: ['_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md', '_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/addendum.md', '_bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md', '_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md', '_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/EXPERIENCE.md']
---

# AzentisERP - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for AzentisERP, decomposing the requirements from the PRD and Architecture Spine into implementable stories. No UX design contract exists — AzentisERP inherits ERPNext's desk UI wholesale rather than building bespoke UI (PRD Non-Goals).

## Requirements Inventory

### Functional Requirements

FR1: The system provides a custom app (Branding App) that overrides product name, logo, favicon, and app metadata at the platform level, without modifying Frappe/ERPNext source files.
FR2: The system allows overriding primary/accent colors, login page styling, and splash/loading screen via the Branding App's stylesheet, included through the standard app-asset hook.
FR3: Email templates (welcome, notifications, password reset) render with the operator's or tenant's brand name and footer text instead of default Frappe/ERPNext text.
FR4: The system provisions a new, independent site per tenant with its own database, isolated from every other tenant's data.
FR5: The system routes incoming requests to the correct tenant site based on the request's domain/subdomain (DNS-based multi-tenancy), so each tenant can use its own domain.
FR6: The system provides a single scripted/automated path that creates a new site, installs the ERPNext fork and Branding App, sets the admin password, and completes initial setup.
FR7: The system provides a per-site configuration capability (Tenant Settings) covering: tenant/company name, logo, favicon, login background, primary/secondary colors, email sender name, email footer text, and custom domain.
FR8: The system reads a site's Tenant Settings on page load and applies that tenant's branding (colors, logo) without requiring a code deployment or restart.
FR9: The system allows enabling or disabling ERPNext modules independently per tenant, reflected by hiding/showing them in the sidebar.
FR10: The system offers named presets (Retail, Services, Manufacturing, General) that set a sensible default `enabled_modules` bundle at onboarding time, without preventing later manual adjustment.
FR11: Given a client name, domain, admin email, module preset, logo, and colors, the system provisions the site, installs and configures branding, enables the selected preset's modules, creates the admin user, and sends a welcome email — as one operator-triggered action.
FR12: The system provisions and renews SSL/TLS certificates for each tenant's domain automatically.
FR13: The system performs at-least-daily automated backups of every tenant's site (database + files) and stores them offsite.
FR14: The production server exposes only ports 80/443 publicly; administrative access (SSH) is restricted.
FR15: All product customizations (branding, tenant config, module toggling) live exclusively in the Branding App and DocType/Custom Field layer — never as edits to Frappe or ERPNext source.
FR16: The system supports testing an upstream merge on a staging site before it is applied to any production tenant site, and applying it fleet-wide only after staging verification.

### NonFunctional Requirements

NFR1: Scalability — the architecture must not require re-architecture to add tenants or servers within the Year-1 target (10-20 tenants); per-tenant DB isolation is the scaling mechanism.
NFR2: Flexibility — new module presets and per-tenant branding/config fields must be addable via configuration (DocType records/fields), not code changes to the Branding App's core logic.
NFR3: Data Isolation & Security — per-tenant data must never be readable/writable cross-tenant; relies on Frappe's existing per-site database isolation, not custom access-control code.
NFR4: Maintainability — every customization must survive an upstream Frappe/ERPNext merge without manual re-application.
NFR5: Availability — no formal uptime SLA is committed to tenants at MVP; baseline reliability (backups, TLS, restricted access) applies regardless.
NFR6: Localization/Compliance — GST-ready accounting (inherited from ERPNext) is required at launch; no other jurisdiction's compliance is targeted.
NFR7: License/IP compliance — GPLv3 license notices and copyright headers must remain intact through every merge; only visible product branding (logos, names, footer/UI text) is replaced.
NFR8: No source modification — Frappe/ERPNext core is never edited for customization; hooks, overrides, and the Branding App are the only extension points.
NFR9: No reimplementation — RBAC, audit logs, REST API, and workflow engine are inherited from Frappe as-is, never rebuilt.
NFR10: Staged verification — every upstream merge is verified on a staging site before touching any production tenant.

### Additional Requirements

- **App scaffold (Epic 1 Story 1 impact):** No greenfield starter template applies — the closest analog is `bench new-app our_brand`, scaffolding the Branding App inside the existing Frappe Bench. This bootstraps the namespace the rest of the platform builds into (AD-1).
- **Design paradigm (governs all epics):** Two-part — Frappe Hook/Plugin Extension for the runtime/app layer (branding, Tenant Settings, module toggling), Idempotent CLI Pipeline for the provisioning/orchestration layer. Dependency direction is one-way: `our_brand` → Frappe/ERPNext APIs, never reverse (AD-1).
- **Data model:** Tenant Settings is a Single DocType (one record per site) holding branding fields + `enabled_modules` as a Table MultiSelect field (child rows referencing canonical Module Def names) (AD-2). Module Preset is its own DocType (name + ordered module list); applying a preset copies its list into Tenant Settings as a snapshot, not a live FK (AD-5).
- **Branding read path:** All branding/module reads go through one accessor using `frappe.get_cached_doc("Tenant Settings")`, auto-invalidated on save — never a scattered raw `frappe.get_single`/`get_doc` call (AD-2/AD-3). Injected as inline CSS custom properties on every page load; never a compiled per-tenant static asset file.
- **Module toggling scope:** `enabled_modules` controls Workspace/sidebar visibility only via a hook — explicitly NOT a permission/RBAC boundary at MVP; does not block direct DocType/API access (AD-4). Full RBAC-level enforcement is out of scope unless a tenant needs internal trust tiers.
- **Module dependency checks:** Warn-only (not hard-block), enforced through exactly one shared function, `our_brand.module_rules.validate_dependencies()`, called by both the preset-apply flow and the manual toggle flow — no duplicated logic (AD-6).
- **Provisioning pipeline (ordered, idempotent, resumable):** (1) create site under canonical internal name → (2) install ERPNext + Branding App → (3) create Tenant Settings → (4) set admin user → (5) request TLS + bind `custom_domain` once DNS resolves (resumable if not yet) → (6) send welcome email. Each step checks its own completion state before acting (AD-7, AD-11).
- **Provisioning invocation:** A `bench` custom command run directly on the production server (operator SSH session) — no hosted/remote onboarding API at MVP (AD-8).
- **Staging environment:** One more site on the same production bench, not a separate server — used exclusively to verify upstream merges before fleet rollout (AD-9).
- **Infrastructure/deployment:** Single production server, Ubuntu 22.04+, min 4GB RAM / 2 vCPU, India-hosted region; Nginx + Gunicorn managed by Supervisor via `bench setup production`; MariaDB + Redis colocated on the same server.
- **Stack pins:** Frappe Framework `version-15` (stock, unforked, from `frappe/frappe`), ERPNext `version-15` (forked under our GitHub org), Python 3.11+, Node.js 20/22 LTS for actual deployment, MariaDB 10.11+, Redis latest stable.
- **Backup mechanism:** Frappe's native S3-compatible backup path (`s3_backup_enabled` + `s3_backup_region` in `site_config.json`), targeting an S3-compatible bucket in `ap-south-1` (Mumbai) — our choice per India data-residency, not a Frappe default (AD-10).
- **Monitoring/logging:** Explicitly deferred beyond MVP — daily backups + manual checks only; no uptime/alerting dashboard at launch.
- **Cross-site data access:** No cross-site DB connections from application/hook code, ever; any platform-wide view is produced by iterating the bench's site list externally, never a live cross-database query.
- **Failure behavior:** Hook failures (e.g. malformed Tenant Settings) fail open to stock/default branding rather than breaking page render for tenant users.

### UX Design Requirements

*(Updated 2026-07-10 — a UX pass ran mid-workflow, after this section was originally written. AzentisERP still inherits ERPNext's desk UI as-is with no redesign; the UX contract below scopes only the branding/theming layer.)*

UX design contract: `ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md` + `EXPERIENCE.md`, both `status: final`. Scoped to the branding/theming layer only (login, splash, navbar accent, transactional email header) — the inherited ERPNext desk UI itself has no UX-DRs.

UX-DR1: Login page and splash screen must support light/dark theme via `prefers-color-scheme`, automatically, no manual toggle. Covered by Story 1.3, Story 1.4.
UX-DR2: Login page and splash screen must be genuinely mobile-responsive (fluid card width, 16px minimum input font-size, 44/48px touch targets, `dvh` viewport unit, safe-area-inset padding) — not just "it shrinks." Covered by Story 1.3.
UX-DR3: Mesh background animation must respect `prefers-reduced-motion: reduce` (disabled entirely, not slowed). Covered by Story 1.3, Story 1.4.
UX-DR4: Glass card must degrade gracefully when `backdrop-filter` is unsupported (near-opaque fallback, never broken/transparent). Covered by Story 1.3.
UX-DR5: Primary button text color must be computed server-side from the tenant's gradient luminance, never hardcoded, so no tenant color pair can produce unreadable text. Covered by Story 1.3.
UX-DR6: `Tenant Settings.login_background` (uploaded image) must override the animated mesh when set, both surfaces, live/no-restart. Covered by Story 1.3, Story 1.7.

All 6 UX-DRs are covered by at least one story (Implementation Readiness Assessment 2026-07-10 confirmed this required amending Epic 1 — see that report for the gap this closed).

### FR Coverage Map

FR1: Epic 1 - Platform-level brand override (Branding App)
FR2: Epic 1 - Visual theming (colors, login page incl. light/dark/mobile/accessibility — Story 1.3; splash screen — Story 1.4)
FR3: Epic 1 - Branded transactional email
FR4: Epic 2 - Isolated per-tenant site
FR5: Epic 2 - DNS-based routing
FR6: Epic 4 - Repeatable provisioning script
FR7: Epic 1 - Tenant Settings record
FR8: Epic 1 - Dynamic per-tenant branding injection
FR9: Epic 3 - Per-tenant module enable/disable
FR10: Epic 3 - Business-type module presets
FR11: Epic 4 - One-action client onboarding
FR12: Epic 4 - TLS for every tenant domain
FR13: Epic 5 - Automated backups
FR14: Epic 5 - Network access control
FR15: Epic 5 - Customization isolation (proven via merge test)
FR16: Epic 5 - Staged rollout of upstream updates

## Epic List

### Epic 1: Branded Single-Instance Platform
Run one Frappe/ERPNext instance where every trace of Frappe/ERPNext branding is replaced by the operator's/tenant's own — logo, colors, login page, emails — driven by data (Tenant Settings) so it changes without a redeploy or restart.
**FRs covered:** FR1, FR2, FR3, FR7, FR8

### Epic 2: Isolated Multi-Tenant Sites
Run multiple client sites on one server, each with its own isolated database, each reachable at its own domain/subdomain, each carrying its own branding from Epic 1.
**FRs covered:** FR4, FR5

### Epic 3: Business-Type Module Scoping
Control exactly which ERP modules a tenant sees, with sensible default bundles (Retail/Services/Manufacturing/General) applied automatically, so SMB clients aren't overwhelmed by irrelevant modules.
**FRs covered:** FR9, FR10

### Epic 4: One-Action Client Onboarding
Onboard a brand-new paying client — site, branding, modules, admin user, TLS, welcome email — in a single action, under 10 minutes, instead of repeating Epics 1–3's steps by hand every time.
**FRs covered:** FR6, FR11, FR12

### Epic 5: Platform Reliability & Upstream Maintainability
Trust that the platform stays online (backups, restricted access) and stays safely patchable against upstream Frappe/ERPNext security releases without breaking any tenant's customizations.
**FRs covered:** FR13, FR14, FR15, FR16

---

## Epic 1: Branded Single-Instance Platform

Run one Frappe/ERPNext instance where every trace of Frappe/ERPNext branding is replaced by the operator's/tenant's own — logo, colors, login page, emails — driven by data (Tenant Settings) so it changes without a redeploy or restart.

**FRs covered:** FR1, FR2, FR3, FR7, FR8
**NFRs relevant:** NFR7 (GPLv3 headers/notices untouched), NFR8 (no core source edits), NFR2 (flexibility — config-driven, not hardcoded)
**Architecture:** AD-1 (fork ERPNext only, stock Frappe Framework; Branding App scaffold, `our_brand`), AD-2 (Tenant Settings Single DocType + cached accessor), AD-3 (live CSS injection, never a compiled asset)

### Story 1.1: Fork ERPNext and Bootstrap the Base Platform

As the platform operator,
I want our own fork of ERPNext running on a Frappe Bench,
So that we have a controlled, mergeable codebase to build every later customization on top of.

**Acceptance Criteria:**

**Given** GitHub org access
**When** ERPNext is forked under our org
**Then** `github.com/OUR_ORG/erpnext` exists as our controlled copy, on the `version-15` branch (PRD §10.7)

**Given** a bench initialized with stock Frappe Framework (`bench init --frappe-branch version-15`, from the official `frappe/frappe` — deliberately NOT forked, per AD-1/PRD §10.7)
**When** `bench get-app erpnext` pulls from our fork's URL
**Then** the bench's installed apps include our forked ERPNext, not a direct pull from the upstream `frappe/erpnext` repo

**Given** a new site on this bench
**When** `install-app erpnext` runs
**Then** the setup wizard completes and all inherited ERPNext modules load, with zero customization applied yet
**And** this story introduces no customization of its own — it is the unmodified inherited foundation every later story in this epic brands on top of (this is the exact point from which AD-1's "core is never modified" starts being a checkable fact, e.g. via `git diff` against upstream)

### Story 1.2: Platform Brand Override

As the platform operator,
I want the app's name, logo, favicon, and metadata replaced platform-wide,
So that no page shows "Frappe" or "ERPNext" as the product name.

**Acceptance Criteria:**

**Given** the base platform from Story 1.1 (forked ERPNext installed, unmodified)
**When** `our_brand` is scaffolded (`bench new-app`) and installed
**Then** `app_name`/`app_title`/`app_publisher`/`app_logo_url` in `hooks.py` reflect our brand, not Frappe's defaults

**Given** `our_brand` is installed
**When** any desk page renders
**Then** no visible string "Frappe" or "ERPNext" appears in the UI chrome

**Given** `our_brand` is uninstalled
**When** the site reloads
**Then** stock Frappe/ERPNext branding returns cleanly, proving isolation (FR15/AD-1)
**And** no file under the Frappe or ERPNext source tree is modified to achieve this (NFR8) — verified via `git diff` against upstream showing zero changes outside `our_brand`

### Story 1.3: Visual Theming — Colors and the Login Page (Light/Dark, Responsive, Accessible)

As the platform operator,
I want primary/accent colors and the login page restyled — including light/dark theme, mobile responsiveness, and accessibility fallbacks,
So that the platform looks like our product, not a generic Frappe install, on any device or system preference a real user actually has.

*(Amended per Implementation Readiness Assessment 2026-07-10 — the finalized UX spines, `DESIGN.md`/`EXPERIENCE.md`, specified several concrete requirements that were never made testable here until now.)*

**Acceptance Criteria:**

**Given** `our_brand`'s stylesheet is included via `app_include_css`
**When** any page loads
**Then** primary/accent colors match our theme

**Given** a user visits the login page
**When** it renders
**Then** it shows our styling, not Frappe's default login template
**And** the footer no longer reads "Built on Frappe/ERPNext" (or equivalent stock text)
**And** no per-tenant static CSS file is generated at this stage — this story is platform-wide only (per-tenant theming is Story 1.7/AD-3)

**Given** the operating system/browser reports `prefers-color-scheme: dark`
**When** the login page renders
**Then** it automatically uses the dark-theme tokens (`DESIGN.md` light/dark surface, text, and glass tokens) — no manual toggle required

**Given** the user has `prefers-reduced-motion: reduce` set
**When** the mesh background renders
**Then** the drift animation is disabled entirely (not merely slowed) — blobs render static

**Given** the browser doesn't support `backdrop-filter`
**When** the login card renders
**Then** it falls back to the near-opaque glass surface token (`DESIGN.md`'s fallback tokens) — never a broken transparent/unreadable card

**Given** any tenant's `primary_color`/`secondary_color` pair, including unusually light or dark combinations
**When** the primary button renders
**Then** its text color is computed server-side from the gradient's relative luminance — never a hardcoded white — so button text is never unreadable regardless of tenant color choice

**Given** a viewport narrower than `md` (768px)
**When** the login page renders
**Then** the card is fluid-width (capped at `DESIGN.md`'s mobile max-width, not the fixed desktop width), every input/checkbox/link meets the 44px minimum touch target (48px for the primary button), input font-size is fixed at 16px minimum (prevents iOS Safari's auto-zoom-on-focus), the background uses `dvh` not `vh`, and `env(safe-area-inset-*)` padding clears notch/home-indicator devices

**Given** a tenant has set `Tenant Settings.login_background` (an uploaded image)
**When** the login page renders
**Then** that image replaces the animated mesh background entirely — blobs suppressed, not layered — while the glass card and all typography/color tokens stay unchanged

**Given** no `login_background` is set (the default for most tenants)
**When** the login page renders
**Then** the animated mesh background renders as normal

### Story 1.4: Splash Screen — Branded Loading Transition

As a tenant's staff user,
I want a branded loading transition between login and the working ERP, not a flash of unstyled content,
So that the branded experience feels continuous, not like it drops back to generic software mid-flow.

*(New story, added per Implementation Readiness Assessment 2026-07-10 — the splash screen was named in Story 1.3's original narrative but never covered by any acceptance criterion.)*

**Acceptance Criteria:**

**Given** login succeeds
**When** the desk UI is still loading
**Then** the splash screen renders the same mesh/glass visual language as the login page (or the tenant's `login_background` image, if set) with a centered logo mark and a loading indicator — no form, no other interactive elements

**Given** the desk UI finishes loading
**When** the splash screen is showing
**Then** it auto-dismisses without requiring any user action

**Given** the desk UI fails to load within a bounded timeout
**When** the splash screen is showing
**Then** it replaces the loading indicator with a plain "Something went wrong loading your workspace. Retry" message and button — still on the mesh/image background, no glass card needed for a single message

**Given** the same light/dark and `prefers-reduced-motion` conditions as Story 1.3
**When** the splash screen renders
**Then** it inherits identical theme and motion behavior — no separate logic duplicated for this surface

### Story 1.5: Branded Transactional Email

As a tenant's staff user,
I want welcome/notification/password-reset emails to carry our brand name and footer,
So that emails don't look like they came from a stranger's product.

**Acceptance Criteria:**

**Given** a password-reset email is triggered
**When** it sends
**Then** the sender name and footer text are ours, not Frappe/ERPNext defaults

**Given** a welcome or generic notification email is triggered
**When** it sends
**Then** the same brand override applies
**And** GPLv3 license notices in any underlying template source remain untouched (NFR7) — only visible brand text changes

### Story 1.6: Tenant Settings Data Model

As the platform operator,
I want a per-site settings record for tenant branding,
So that a tenant's identity is stored as data, not hardcoded per install.

**Acceptance Criteria:**

**Given** `our_brand` is installed on a site
**When** it's set up
**Then** a Tenant Settings Single DocType exists with fields: `tenant_name`, `site_name`, `custom_domain`, `logo`, `favicon`, `login_background`, `primary_color`, `secondary_color`, `email_sender_name`, `email_footer_text` (AD-2)
**And** `enabled_modules` is deliberately NOT added yet — that's Epic 3's concern (create tables/entities only when needed)

**Given** Tenant Settings is saved
**When** any code reads it
**Then** it goes through one accessor (`frappe.get_cached_doc`), never a scattered raw doc-get call (AD-2)

### Story 1.7: Dynamic Per-Tenant Branding Injection

As a tenant's staff user,
I want the page to reflect my business's colors and logo immediately after an admin changes them,
So that branding updates don't require anyone to touch a server.

**Acceptance Criteria:**

**Given** Tenant Settings' `primary_color` is changed and saved
**When** the next page loads
**Then** the new color renders as an inline CSS custom property — no `bench build`, no restart (FR8, AD-3)

**Given** Tenant Settings has no record yet or a malformed one
**When** a page loads
**Then** it fails open to stock/default branding rather than breaking the page (spine's fail-open convention)
**And** no per-tenant compiled CSS file is ever written to disk (AD-3's explicit prohibition)

**Given** `login_background` is changed (set, cleared, or swapped) and saved
**When** the login page next loads
**Then** it reflects the change immediately — the same live-injection, no-restart rule Story 1.3 relies on applies identically to the background image, not just colors

---

## Epic 2: Isolated Multi-Tenant Sites

Run multiple client sites on one server, each with its own isolated database, each reachable at its own domain/subdomain, each carrying its own branding from Epic 1.

**FRs covered:** FR4, FR5
**NFRs relevant:** NFR1 (Scalability — DB-per-tenant is the scaling mechanism), NFR3 (Data Isolation & Security)
**Architecture:** deployment topology (T1, T2…TN each own DB on one bench), Consistency Conventions (site name = canonical internal identifier, distinct from `custom_domain` — AD-11), "no cross-site DB connections, ever" rule

### Story 2.1: Enable DNS-Based Multi-Tenant Routing

As the platform operator,
I want the bench to route incoming requests to the correct site by domain,
So that each tenant can be reached at its own address.

**Acceptance Criteria:**

**Given** `dns_multitenant` is enabled on the bench
**When** a request arrives for a given hostname
**Then** it's routed to the matching site's database and assets (FR5)

**Given** two different tenant hostnames
**When** each is requested
**Then** each resolves to its own distinct site — no fallback to a default/wrong site

### Story 2.2: Create an Isolated Tenant Site

As the platform operator,
I want each new tenant to get a fully separate site and database,
So that one client's data can never leak into another's.

**Acceptance Criteria:**

**Given** a new tenant is provisioned
**When** the site is created
**Then** it gets its own isolated database — no shared tables with any other tenant (FR4, NFR3)

**Given** the site name assigned at creation
**When** it's inspected
**Then** it's the tenant's canonical internal identifier (`{tenant-slug}.{platform-domain}`), not necessarily the client's eventual public domain — the two are related but distinct (AD-11), so this story doesn't block on a client's DNS being ready

**Given** two tenant sites exist
**When** a query is run as one tenant's admin
**Then** it cannot read or write the other tenant's records under any tested path (NFR3)

### Story 2.3: Tenant Site Carries Its Own Branding

As the platform operator,
I want a newly created tenant site to work with Epic 1's branding system independently,
So that adding a tenant doesn't require any branding rework.

**Acceptance Criteria:**

**Given** a new tenant site has ERPNext and `our_brand` installed on it
**When** it's accessed
**Then** it has its own independent Tenant Settings record (Story 1.6), separate from every other tenant's

**Given** two tenants each set different `primary_color` values
**When** each is viewed
**Then** each shows only its own color — no cross-tenant branding bleed
**And** no platform-wide view queries across tenant databases to produce this — each site is inspected independently (spine's "no cross-site DB connections" rule)

---

## Epic 3: Business-Type Module Scoping

Control exactly which ERP modules a tenant sees, with sensible default bundles (Retail/Services/Manufacturing/General) applied automatically, so SMB clients aren't overwhelmed by irrelevant modules.

**FRs covered:** FR9, FR10
**Architecture:** AD-4 (nav-level toggling, not RBAC), AD-5 (presets are data, snapshot-copied not live FK), AD-6 (warn-only dependency checks via one shared function)

### Story 3.1: Add Module Toggling to Tenant Settings

As the platform operator,
I want Tenant Settings to hold a per-tenant list of enabled modules,
So that module visibility becomes tenant-configurable data, not a code path.

**Acceptance Criteria:**

**Given** Tenant Settings (Story 1.6)
**When** the `enabled_modules` Table MultiSelect field is added
**Then** it references canonical Module Def names (AD-2's data-shape rule)

**Given** a tenant with no `enabled_modules` set yet (new tenant, empty)
**When** the sidebar renders
**Then** it fails open to showing all modules — never fails closed to showing none (consistent with Epic 1's fail-open convention)

### Story 3.2: Filter Sidebar by Enabled Modules

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
**Then** it reflects the change without a restart (reuses Story 1.6's cached-accessor pattern)

### Story 3.3: Module Preset Data Model

As the platform operator,
I want business-type presets stored as data,
So that adding a fifth preset later never requires a code change.

**Acceptance Criteria:**

**Given** the Module Preset DocType
**When** it's created
**Then** it holds `preset_name` + an ordered `modules` list in the same Table MultiSelect shape as `enabled_modules` (AD-5)

### Story 3.4: Seed the Four Business-Type Presets

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

### Story 3.5: Warn on Module Dependency Violations

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

---

## Epic 4: One-Action Client Onboarding

Onboard a brand-new paying client — site, branding, modules, admin user, TLS, welcome email — in a single action, under 10 minutes, instead of repeating Epics 1–3's steps by hand every time.

**FRs covered:** FR6, FR11, FR12
**Architecture:** AD-7 (idempotent resumable pipeline), AD-8 (SSH-run CLI, no hosted API), AD-11 (TLS + domain-alias as separate resumable steps)

### Story 4.1: Stand Up Production Server Infrastructure

As the platform operator,
I want a real production server running the bench in production mode,
So that a real client can actually be onboarded onto working infrastructure, not just a local dev bench.

**Acceptance Criteria:**

**Given** an Ubuntu 22.04+ server (min 4GB RAM / 2 vCPU, India-hosted region per PRD §10.4)
**When** `bench setup production {user}` runs
**Then** Nginx, Gunicorn, and Supervisor are configured and the bench serves requests over HTTP

**Given** this story completes
**When** Epic 5's later stories (backups, firewall) run
**Then** they build on this same server — this story is not repeated per-tenant, it happens once

### Story 4.2: One-Action Provisioning Pipeline — Site, Branding, Modules, Admin

As the platform operator,
I want one command that creates a fully configured tenant site,
So that I never repeat Epics 1–3's setup steps by hand per client.

**Acceptance Criteria:**

**Given** client name, domain, admin email, module preset, logo, and colors
**When** the pipeline runs
**Then** it creates the site (canonical internal name, AD-11), installs ERPNext + `our_brand`, creates a populated Tenant Settings record, applies the selected preset (Story 3.4), and sets the admin user — as one operator-triggered action (FR6, FR11)

**Given** a partial failure mid-pipeline (e.g., site created but app install fails)
**When** the pipeline is re-run
**Then** it resumes safely from the failed step rather than erroring or duplicating work (AD-7)

**Given** this story's steps complete (excluding TLS/email, Stories 4.3–4.4)
**When** elapsed time is measured
**Then** it's well under the 10-minute SM-2 target on its own

### Story 4.3: TLS Issuance and Custom Domain Binding

As the platform operator,
I want TLS and the client's real domain wired up as part of onboarding,
So that a client never lands on an insecure or wrong-domain site.

**Acceptance Criteria:**

**Given** a newly provisioned site (Story 4.2)
**When** its `custom_domain`'s DNS already resolves
**Then** TLS is requested and the domain is bound automatically (FR12, AD-11)

**Given** DNS isn't resolving yet
**When** the pipeline runs
**Then** this step is skipped without blocking the rest of onboarding, and is safely re-runnable later once DNS is ready (UJ-1's explicit edge case)

### Story 4.4: Send Branded Welcome Email

As a new tenant's admin,
I want a branded welcome email with my login link,
So that I can access my instance without asking Ajit for help.

**Acceptance Criteria:**

**Given** onboarding completes (Stories 4.2–4.3)
**When** the welcome email step runs
**Then** it sends using Epic 1's branded template (Story 1.5) with a working login link

**Given** outbound email transport isn't configured on the server (a one-time ops precondition, previously left unstated in the architecture spine's Deferred list)
**When** this step runs without it
**Then** it fails loudly and is clearly reported — never silently completing onboarding while the client never receives their link

---

## Epic 5: Platform Reliability & Upstream Maintainability

Trust that the platform stays online (backups, restricted access) and stays safely patchable against upstream Frappe/ERPNext security releases without breaking any tenant's customizations.

**FRs covered:** FR13, FR14, FR15, FR16
**Architecture:** AD-9 (staging = one more site on the production bench), AD-10 (S3-compatible backups, India region)

### Story 5.1: Automated Offsite Backups

As the platform operator,
I want every tenant site backed up daily to offsite storage,
So that a server failure never means losing a client's data.

**Acceptance Criteria:**

**Given** an S3-compatible bucket configured in `ap-south-1` (a one-time ops precondition — bucket/credentials must exist before this story can pass, not silently assumed)
**When** the daily backup cron runs
**Then** every tenant site's database and files are backed up and land in that bucket (FR13, AD-10)

**Given** a backup exists
**When** a restore is attempted
**Then** the tenant's site can be restored without data loss beyond the backup interval

### Story 5.2: Restrict Network Access

As the platform operator,
I want the production server to expose only what's necessary,
So the attack surface stays minimal.

**Acceptance Criteria:**

**Given** the production server (Story 4.1)
**When** firewall rules are applied
**Then** only ports 80/443 are publicly reachable and SSH access is restricted (FR14)

**Given** the firewall is applied
**When** any other port is probed from outside the server (e.g., a database or bench-internal port)
**Then** it does not respond — verified as a negative-path check, not just assumed from the allow-list configuration

### Story 5.3: Create and Maintain a Staging Site

As the platform operator,
I want a staging site on the same production bench,
So that I have somewhere safe to test upstream changes before they touch a paying client.

**Acceptance Criteria:**

**Given** the production bench (Story 4.1)
**When** a staging site is created
**Then** it exists as one more site on that same bench — not a separate server (AD-9) — and mirrors the customization stack (`our_brand` + ERPNext fork) any tenant site would have

### Story 5.4: Staged Upstream Update Rollout

As the platform operator,
I want to verify an upstream Frappe/ERPNext update on staging before it touches any tenant,
So a bad update never hits a paying client first.

**Acceptance Criteria:**

**Given** a new upstream ERPNext/Frappe release
**When** `git fetch upstream && git merge upstream/version-15` runs against the fork
**Then** it's applied and tested on the staging site (Story 5.3) first

**Given** staging verification passes
**When** the update is rolled out
**Then** it's applied to production tenant sites only after that verification — never before (FR16)

### Story 5.5: Prove Customization Isolation via a Real Merge

As the platform operator,
I want direct evidence that our customizations survive an upstream merge,
So "isolation" isn't just a design intention.

**Acceptance Criteria:**

**Given** a real upstream merge is performed (Story 5.4's process, on staging)
**When** the merge completes
**Then** it produces zero or near-zero conflicts outside the `our_brand` app directory (FR15's stated testable consequence) — and any conflict that does occur is documented as a precedent for future merges
