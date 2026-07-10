---
epic: 1
title: Branded Single-Instance Platform
status: approved
source: ../../epics.md
---

# Epic 1: Branded Single-Instance Platform

Run one Frappe/ERPNext instance where every trace of Frappe/ERPNext branding is replaced by the operator's/tenant's own — logo, colors, login page, emails — driven by data (Tenant Settings) so it changes without a redeploy or restart.

**FRs covered:** FR1, FR2, FR3, FR7, FR8
**NFRs relevant:** NFR7 (GPLv3 headers/notices untouched), NFR8 (no core source edits), NFR2 (flexibility — config-driven, not hardcoded)
**Architecture:** AD-1 (fork ERPNext only, stock Frappe Framework; Branding App scaffold, `our_brand`), AD-2 (Tenant Settings Single DocType + cached accessor), AD-3 (live CSS injection, never a compiled asset)

## Story 1.1: Fork ERPNext and Bootstrap the Base Platform

As the platform operator,
I want our own fork of ERPNext running on a Frappe Bench,
So that we have a controlled, mergeable codebase to build every later customization on top of.

**Acceptance Criteria:**

**Given** GitHub org access
**When** ERPNext is forked under our org
**Then** `github.com/ajitzagade/erpnext` exists as our controlled copy, on the `version-15` branch (PRD §10.7)

**Given** a bench initialized with stock Frappe Framework (`bench init --frappe-branch version-15`, from the official `frappe/frappe` — deliberately NOT forked, per AD-1/PRD §10.7)
**When** `bench get-app erpnext` pulls from our fork's URL
**Then** the bench's installed apps include our forked ERPNext, not a direct pull from the upstream `frappe/erpnext` repo

**Given** a new site on this bench
**When** `install-app erpnext` runs
**Then** the setup wizard completes and all inherited ERPNext modules load, with zero customization applied yet
**And** this story introduces no customization of its own — it is the unmodified inherited foundation every later story in this epic brands on top of (this is the exact point from which AD-1's "core is never modified" starts being a checkable fact, e.g. via `git diff` against upstream)

## Story 1.2: Platform Brand Override

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

## Story 1.3: Visual Theming — Colors and the Login Page (Light/Dark, Responsive, Accessible)

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

## Story 1.4: Splash Screen — Branded Loading Transition

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

## Story 1.5: Branded Transactional Email

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

## Story 1.6: Tenant Settings Data Model

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

## Story 1.7: Dynamic Per-Tenant Branding Injection

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
