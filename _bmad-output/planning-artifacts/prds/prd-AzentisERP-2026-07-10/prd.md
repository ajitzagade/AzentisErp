---
title: AzentisERP
status: final
created: 2026-07-10
updated: 2026-07-10
---

# PRD: AzentisERP
*Working title — confirm final product/brand name.*

## 0. Document Purpose

This PRD scopes AzentisERP: a rebranded, self-hosted, multi-tenant ERP/CRM SaaS platform built by forking Frappe Framework and ERPNext (GPLv3). It is written for the builder (solo, AI-assisted) and doubles as the spine for downstream Architecture and Epics/Stories work. Terms are Glossary-anchored (§3); functional requirements are grouped by feature (§4) and numbered globally (FR-1…); inferred content is tagged inline `[ASSUMPTION]` and indexed in §9. The step-by-step technical mechanics (bench commands, DocType field lists, hooks.py structure, architecture diagram) already captured in `docs/product.md` are preserved verbatim in `addendum.md` — this PRD describes *what* the system must do, not *how* the fork implements it.

## 1. Vision

AzentisERP lets small and medium Indian businesses run their operations — sales, purchasing, accounting, inventory, HR, projects — on a modern ERP/CRM without touching the Frappe/ERPNext name, paying enterprise-implementation prices, or drowning in modules they don't use. It inherits ERPNext's mature, audited functionality wholesale (RBAC, workflow engine, audit log, GST-ready accounting) rather than rebuilding it, and adds exactly one new layer: a multi-tenant provisioning and branding system that lets one solo operator spin up a fully white-labelled, module-scoped instance for a new client in under ten minutes.

The product's differentiation is not the ERP functionality itself — it's the speed, cost, and polish of getting a branded, right-sized instance live for a paying SMB client, and keeping it live and patchable without per-client engineering effort.

## 2. Target User

### 2.1 Jobs To Be Done

- **As the platform operator** (solo, AI-assisted), I need to onboard a new SMB client to a fully working, branded ERP instance in minutes, not weeks, so I can reach 10-20 paying tenants within the first year without hiring.
- **As an SMB business owner** (retail, services, or manufacturing, India-based), I need affordable, GST-ready business software that carries *my* brand and only shows the modules relevant to *my* business, so my staff aren't overwhelmed by an unfamiliar tool that looks like someone else's product.
- **As a tenant's staff user** (accountant, salesperson, warehouse clerk), I need the day-to-day ERP experience (already provided by ERPNext) to work reliably and stay isolated from every other tenant's data.

### 2.2 Non-Users (v1)

- Enterprises needing deep custom module development beyond Custom Fields/DocTypes — out of scope; this platform is standard-module SMB-focused.
- Non-Indian clients — GST-centric accounting and India-first positioning mean international tax/localization is not a v1 target. `[ASSUMPTION: India-only launch; revisit if a non-Indian client is prospected.]`
- Clients requiring on-premise (self-managed, non-hosted-by-us) deployment.

### 2.3 Key User Journeys

- **UJ-1. Ajit onboards a new retail client in under ten minutes.**
  - **Persona + context:** Ajit, the solo platform operator, has just closed a deal with a small retail shop owner.
  - **Entry state:** Authenticated on the management server via CLI/admin command; has the client's name, domain, admin email, and logo on hand.
  - **Path:** Runs the onboarding command with client details and the "Retail" module preset → system provisions an isolated site, installs ERPNext + the branding app, applies the client's logo/colors, enables only Retail-relevant modules, creates the admin user, sends a welcome email.
  - **Climax:** Total elapsed time is under 10 minutes; the client receives a login link to a fully branded, right-sized instance with no manual follow-up work from Ajit.
  - **Resolution:** Client logs in, sees their own brand and only Stock/POS/Accounts/CRM in the sidebar — no trace of Frappe or ERPNext.
  - **Edge case:** Domain/DNS isn't yet pointed at the server — provisioning still succeeds against the subdomain/localhost pattern, and Ajit reconfigures DNS separately without redoing the site setup.

- **UJ-2. A shop owner logs into her own branded ERP for the first time.**
  - **Persona + context:** Priya owns a small retail shop in Pune, has just been onboarded by Ajit, and has never used ERPNext or heard of Frappe.
  - **Entry state:** Receives a welcome email with a login link to her subdomain/custom domain.
  - **Path:** Clicks the link → sees a login page styled with her business's colors and logo (not a generic Frappe login) → logs in → sidebar shows only the modules in her preset (Stock, POS, Accounts, CRM).
  - **Climax:** Nothing in the UI — login page, navbar, footer, emails — reveals this is built on Frappe/ERPNext; it feels like software made for her business.
  - **Resolution:** She starts entering her first product/customer without needing onboarding help.

- **UJ-3. Ajit rolls out an upstream ERPNext security patch across all tenants.**
  - **Persona + context:** Ajit, now running 15 tenant sites, is notified of an upstream ERPNext security release.
  - **Entry state:** On the management server, staging site available.
  - **Path:** Merges upstream into the fork → tests on staging → runs the update across all tenant sites.
  - **Climax:** All 15 sites patch successfully with zero branding regressions, because customizations live entirely in the separate `our_brand` app.
  - **Resolution:** Patch confirmed applied fleet-wide; incident (if any) closed.
  - **Edge case:** A merge conflict appears in `our_brand`-adjacent hook code — Ajit resolves it once, centrally, rather than per-tenant.

## 3. Glossary

- **Tenant** — One client business using an isolated site (own database, own domain/subdomain, own branding and enabled-module set).
- **Site** — A Frappe Bench-managed instance bound to a tenant; one site per tenant, isolated database.
- **Bench** — The shared Frappe Bench installation hosting all tenant sites on one server (shared codebase: Frappe Framework, the ERPNext fork, the branding app).
- **Branding App** *(working name: `our_brand`, final app name TBD)* — The custom Frappe app holding all white-label customizations (CSS, logo, email templates, login page), kept separate from Frappe/ERPNext source so upstream updates stay mergeable.
- **Tenant Settings** — A per-site configuration record (DocType) holding a tenant's branding (logo, colors, favicon) and `enabled_modules`.
- **Module Preset** — A named bundle of `enabled_modules` matching a common business type (Retail, Services, Manufacturing, General) applied at onboarding.
- **Provisioning** — The automated process of creating a new tenant site, installing apps, applying branding, enabling modules, and creating the admin user.
- **Upstream** — The original Frappe Framework and ERPNext open-source projects this platform forks from and periodically merges updates from.

## 4. Features

### 4.1 Brand Identity & White-Labelling

**Description:** All Frappe/ERPNext product branding (name, logo, colors, login page, navbar, footer, email templates, splash screen) is replaced with the operator's/tenant's own, entirely via the separate Branding App — never by editing Frappe/ERPNext source. Realizes UJ-2.

#### FR-1: Platform-level brand override
The system provides a custom app (Branding App) that overrides product name, logo, favicon, and app metadata at the platform level, without modifying Frappe/ERPNext source files.

**Consequences (testable):**
- No string "Frappe" or "ERPNext" is visible anywhere in the desk UI, login page, navbar, or footer after Branding App install.
- Uninstalling the Branding App restores stock Frappe/ERPNext branding cleanly (proves separation).

#### FR-2: Visual theming (colors, login, footer, splash)
The system allows overriding primary/accent colors, login page styling, and splash/loading screen via the Branding App's stylesheet, included through the standard app-asset hook. The login page and splash screen support both light and dark theme (following system preference automatically) and are genuinely usable on mobile viewports, not just visually scaled down. *(Amended 2026-07-10 — dark/light and mobile-first were committed decisions from the UX pass, `ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md`+`EXPERIENCE.md`, but were missing from this FR's original text; added here per the Implementation Readiness Assessment so the PRD remains the accurate source of truth.)*

#### FR-3: Branded transactional email
Email templates (welcome, notifications, password reset) render with the operator's or tenant's brand name and footer text instead of default Frappe/ERPNext text.

**Feature-specific NFRs:**
- All license notices and copyright headers in Frappe/ERPNext source remain untouched — only visible product branding is replaced. Realizes the GPLv3 constraint in §Constraints.

### 4.2 Multi-Tenant Site Provisioning

**Description:** Each tenant runs on its own isolated site (own database) within one shared Bench/server, addressable by its own domain or subdomain. Realizes UJ-1.

#### FR-4: Isolated per-tenant site
The system provisions a new, independent site per tenant with its own database, isolated from every other tenant's data.

**Consequences (testable):**
- A query or action performed as Tenant A's admin cannot read or write Tenant B's records under any tested path.
- Deleting or corrupting one tenant's site does not affect any other tenant's availability.

#### FR-5: DNS-based routing
The system routes incoming requests to the correct tenant site based on the request's domain/subdomain (DNS-based multi-tenancy), so each tenant can use its own domain.

#### FR-6: Repeatable provisioning script
The system provides a single scripted/automated path (not manual per-step CLI work) that creates a new site, installs the ERPNext fork and Branding App, sets the admin password, and completes initial setup.

**Out of Scope:** Multi-server / geographically distributed provisioning — single shared server is the MVP target (§6).

### 4.3 Per-Tenant Configuration & Dynamic Branding

**Description:** Beyond platform-wide branding (§4.1), each tenant can carry its own logo, colors, and identity independent of other tenants, configured through data (Tenant Settings) rather than code changes. Realizes UJ-2.

#### FR-7: Tenant Settings record
The system provides a per-site configuration capability (Tenant Settings) covering: tenant/company name, logo, favicon, login background, primary/secondary colors, email sender name, email footer text, and custom domain.

#### FR-8: Dynamic per-tenant branding injection
The system reads a site's Tenant Settings on page load and applies that tenant's branding (colors, logo, and login background image when set) without requiring a code deployment or restart.

**Consequences (testable):**
- Changing a tenant's primary color in Tenant Settings is visibly reflected on next page load, with no bench restart or redeploy.

### 4.4 Module Management & Business-Type Presets

**Description:** A tenant sees only the ERP modules relevant to their business, controlled per-tenant without code changes. Realizes UJ-1, UJ-2.

#### FR-9: Per-tenant module enable/disable
The system allows enabling or disabling ERPNext modules (CRM, Sales, Purchasing, Accounting, HR, Inventory, Projects, Manufacturing, Assets, Support, Website, Workflows, Reports) independently per tenant, reflected by hiding/showing them in the sidebar.

**Consequences (testable):**
- A module disabled for a tenant does not appear in that tenant's sidebar/navigation.
- Enabling/disabling a module does not require a code change or app reinstall.

#### FR-10: Business-type module presets
The system offers named presets (Retail, Services, Manufacturing, General) that set a sensible default `enabled_modules` bundle at onboarding time, without preventing later manual adjustment.

**Consequences (testable):**
- Applying the "Retail" preset enables exactly Stock, POS, Accounts, CRM and disables all other toggleable modules, unless manually overridden afterward.

**Notes:** Inter-module dependencies (e.g., Sales requires Accounting) must be documented and should not be silently violated by preset or manual toggling — see NFR in §Cross-Cutting NFRs and SM-C2 in §7. `[NOTE FOR PM: full dependency validation logic — hard-block vs. warn-only — undecided; flagged as Open Question 6.]`

### 4.5 Client Onboarding Automation

**Description:** The entire path from "signed client" to "client logging into their branded instance" is a single automated action, not a manual multi-step checklist. Realizes UJ-1.

#### FR-11: One-action client onboarding
Given a client name, domain, admin email, module preset, logo, and colors, the system provisions the site, installs and configures branding, enables the selected preset's modules, creates the admin user, and sends a welcome email — as one operator-triggered action.

**Consequences (testable):**
- End-to-end elapsed time from triggering onboarding to the client receiving a working login link is under 10 minutes (SM-2).

**Out of Scope:** A full self-service signup UI where clients onboard themselves without operator involvement — MVP is operator-triggered (§6).

### 4.6 Production Operations & Reliability

**Description:** The platform runs on a production server with the baseline reliability practices a paying client expects: encrypted transport, backups, and access control. Realizes UJ-1, UJ-3.

#### FR-12: TLS for every tenant domain
The system provisions and renews SSL/TLS certificates for each tenant's domain automatically.

#### FR-13: Automated backups
The system performs at-least-daily automated backups of every tenant's site (database + files) and stores them offsite.

**Consequences (testable):**
- A tenant's site can be restored from the most recent offsite backup without data loss beyond the backup interval.

#### FR-14: Network access control
The production server exposes only ports 80/443 publicly; administrative access (SSH) is restricted.

**Feature-specific NFRs:**
- Uptime monitoring and resource (disk/memory) alerting are desirable but deferred beyond MVP — see §6.2.

### 4.7 Upstream Update & Maintainability

**Description:** Because AzentisERP is a fork, not a from-scratch product, its long-term viability depends on staying mergeable with upstream Frappe/ERPNext without re-doing customization work. Realizes UJ-3.

#### FR-15: Customization isolation
All product customizations (branding, tenant config, module toggling) live exclusively in the Branding App and DocType/Custom Field layer — never as edits to Frappe or ERPNext source.

**Consequences (testable):**
- An upstream `git merge` of a new Frappe/ERPNext release produces zero or near-zero conflicts outside the Branding App.

#### FR-16: Staged rollout of upstream updates
The system supports testing an upstream merge on a staging site before it is applied to any production tenant site, and applying it fleet-wide only after staging verification.

**Feature-specific NFRs:**
- GPLv3 license notices and copyright headers must remain intact through every merge (constraint, not a testable FR by itself — see §Constraints).

## 5. Non-Goals (Explicit)

- AzentisERP will not modify Frappe or ERPNext core source for any customization — everything ships through the Branding App, hooks, Custom Fields, and Custom DocTypes.
- AzentisERP will not rebuild RBAC, audit logging, workflow engine, or the REST API — these are inherited from Frappe as-is.
- AzentisERP will not target non-Indian tax/compliance regimes in v1.
- AzentisERP will not offer fully self-service client signup (no operator involvement) in v1 — onboarding is operator-triggered (FR-11).
- AzentisERP will not run multi-server/HA infrastructure in v1 — single production server is the target (§6).

## 6. MVP Scope

**`[NOTE FOR PM]`** The full 8-phase plan in `docs/product.md` (and mirrored in `addendum.md`) is the complete long-term build. Given a **solo, AI-assisted builder targeting a 1-month launch**, the cut below is what this PRD treats as MVP-required; the rest is explicitly deferred. **This split is an `[ASSUMPTION]` — confirm before Architecture/Epics work begins** (Open Question 1).

### 6.1 In Scope (MVP)
- Local dev environment + forked ERPNext installable (Phase 1 of `docs/product.md`).
- Full Branding App: logo, colors, login page, navbar/footer, email templates (FR-1–FR-3).
- DNS-based multi-tenancy with isolated per-tenant sites (FR-4–FR-6).
- Tenant Settings DocType + dynamic branding injection (FR-7–FR-8).
- Module toggling engine + **at least one** business-type preset (recommend "General" plus one vertical preset matching the first prospective client) (FR-9–FR-10).
- Single-action onboarding script/admin command achieving <10 minute provisioning (FR-11).
- Baseline production hardening: SSL per site, daily backups to offsite storage, firewall (FR-12–FR-14).
- Customization isolation in the Branding App, proven via one clean upstream merge test (FR-15).

### 6.2 Out of Scope for MVP
- All four module presets fully built out and tested — ship with 1-2 presets, add the rest as real clients need them. *(v1.1)*
- Uptime monitoring / disk-memory alerting dashboard — daily backups + manual checks suffice at 10-20 tenants. *(v1.1)*
- Self-service admin panel UI for onboarding (beyond a CLI/scripted command) — build once volume justifies it. *(v1.1)*
- Multi-server / high-availability deployment — single server supports the Year-1 10-20 tenant target. *(v2)*
- Formal staged upstream-update tooling/automation (Phase 8) — do the first 1-2 merges manually to learn the real conflict surface before automating. *(v1.1)*
- Non-GST/international localization. *(not planned)*

## 7. Success Metrics

**Primary**
- **SM-1**: 10-20 paying SMB tenants onboarded within Year 1. Validates FR-11 (onboarding automation) and the overall platform value proposition. `[ASSUMPTION: "Year 1" window taken from the stated target; exact cadence/milestones not yet broken down — Open Question 1.]`
- **SM-2**: New client provisioning time under 10 minutes, end-to-end. Validates FR-11.
- **SM-3**: 100% of tenant-facing surfaces (UI, login, email) show zero Frappe/ERPNext branding. Validates FR-1–FR-3.

**Secondary**
- **SM-4**: Zero cross-tenant data isolation incidents. Validates FR-4.
- **SM-5**: Upstream Frappe/ERPNext releases mergeable with near-zero conflict outside the Branding App. Validates FR-15–FR-16.

**Counter-metrics (do not optimize)**
- **SM-C1**: Onboarding speed (SM-2) must not be achieved by skipping admin password strength requirements or setup validation. Counterbalances SM-2.
- **SM-C2**: Module preset simplicity (FR-10) must not silently disable a module another enabled module depends on (e.g., hiding Accounting while Sales stays enabled). Counterbalances FR-9/FR-10.

## Cross-Cutting NFRs

- **Scalability** — The architecture must not block growth past the Year-1 target (10-20 tenants) onto significantly more tenants on the same or additional shared servers; per-tenant DB isolation is the chosen mechanism and must not be revisited to scale further. `[ASSUMPTION: "scalable" interpreted as "does not require re-architecture to add tenants or servers," not as a specific throughput/concurrency SLA — no concurrency target was given (Open Question 1/3).]`
- **Flexibility** — New module presets, and new per-tenant branding/config fields, must be addable via configuration (DocType fields, preset definitions) without code changes to the Branding App's core logic.
- **Data Isolation & Security** — Per-tenant data must never be readable/writable cross-tenant; relies on Frappe's existing per-site database isolation, not custom access-control code.
- **Maintainability** — Every customization must survive an upstream Frappe/ERPNext merge without manual re-application (realizes FR-15).
- **Availability** — No formal uptime SLA is committed to tenants in v1 (informal SMB relationships); baseline reliability (backups, TLS, restricted access) applies regardless. `[ASSUMPTION — Open Question 3.]`
- **Localization/Compliance** — GST-ready accounting (inherited from ERPNext) is required at launch; no other jurisdiction's compliance is targeted.

## Constraints and Guardrails

- Do not edit Frappe or ERPNext source for any customization — use hooks, overrides, and the Branding App exclusively.
- Do not remove or alter GPLv3 license files or copyright headers anywhere in the codebase — only visible product branding (logos, names, footer/UI text) is replaced.
- Do not rebuild functionality Frappe already provides (RBAC, audit logs, REST API, workflow engine) — configure and extend, don't reimplement.
- Prefer Custom Fields and Custom DocTypes (via UI) over code-level forks for client-specific customization needs.
- Every upstream merge must be verified on a staging site before touching any production tenant.

## Monetization

Pricing is **flexible, negotiated per client** rather than a fixed published tier list — exact mechanics (flat fee vs. per-user vs. per-module-tier, contract length, trial terms) are undecided. `[ASSUMPTION: treated as an open business decision, not a system requirement — no FR depends on a specific pricing model. Flagged as Open Question 2.]`

## Data Governance

- Each tenant's data lives in its own isolated database (FR-4); no shared tables across tenants.
- Backups are stored offsite (FR-13); backup storage location/provider not yet chosen.
- Data residency (India-hosted infrastructure vs. any region) not yet decided — relevant given GST/financial data. `[ASSUMPTION — Open Question 4.]`

## Operational Requirements

- Minimum daily backup cadence per tenant site (FR-13).
- TLS on every tenant domain, auto-renewed (FR-12).
- SSH restricted; only 80/443 exposed (FR-14).
- No formal SLA at MVP (see Availability NFR above); revisit once tenant count or contract terms require one.

## Integration and Dependencies

- **ERPNext** is forked under our GitHub org (`version-15` branch, `bench get-app erpnext https://github.com/OUR_ORG/erpnext`). **Frappe Framework itself is *not* forked** — installed from the official `frappe/frappe` repo via `bench init --frappe-branch version-15` — because no customization touches the framework layer; only the ERPNext app layer and the separate Branding App carry customization. *(Resolved decision — see §10.)*
- **MariaDB**, **Redis**, **Nginx/Gunicorn/Supervisor** are inherited infrastructure dependencies from the Frappe stack (see `addendum.md` for versions/config).
- Upstream release cadence is out of this platform's control; §4.7 (FR-15/16) governs how updates are absorbed.

## 8. Open Questions

*(Resolved with defaults for MVP — see §10. Retained here for traceability; revisit if a default proves wrong.)*

1. ~~MVP phasing confirmation~~ — **Resolved:** §6.1/6.2 cut stands as MVP scope.
2. ~~Pricing mechanics~~ — **Resolved (default):** case-by-case negotiation per client; no fixed tier menu at MVP.
3. ~~SLA/uptime commitment~~ — **Resolved (default):** no formal SLA at MVP.
4. ~~Data residency~~ — **Resolved (default):** host in India (Indian cloud region), matching the India-first GST-focused market. Confirm final provider/region at Phase 6 deployment time.
5. ~~Launch vertical~~ — **Resolved (default):** ship "General" preset first; the second (vertical) preset is decided operationally by whichever business type the first real client is, not pre-committed now.
6. ~~Module dependency enforcement~~ — **Resolved (default):** warn-only (documented dependencies, no hard block) at MVP; hard enforcement is a v1.1 candidate if warn-only proves insufficient.

## 9. Assumptions Index

- §2.2 — India-only launch; no non-Indian localization planned for v1.
- §6 — MVP scope cut (full Branding App + multi-tenancy + Tenant Settings + ≥1 preset + baseline prod hardening) vs. deferred items (full preset catalog, monitoring dashboard, self-service admin UI, HA, update automation) — confirmed given the 1-month solo timeline (§10).
- §7 SM-1 — "Year 1" window and lack of interim milestones taken as-is from the stated target.
- §Cross-Cutting NFRs (Scalability) — interpreted as "no re-architecture needed to add tenants/servers," not a specific concurrency/throughput number.
- §Cross-Cutting NFRs (Availability) — no formal SLA assumed for MVP (§10.3).
- §Monetization — pricing model treated as an open business decision outside system requirements (§10.2).
- §Data Governance — data residency resolved to India-hosted (§10.4).
- §Integration and Dependencies — only ERPNext is forked at the repo level; Frappe Framework is used stock from upstream (§10.7).

## 10. Resolved Decisions (locked in to unblock Architecture)

Made explicitly to keep the 1-month solo timeline moving; each is a default, not a permanent commitment — revisit if evidence says otherwise.

1. **MVP phasing** — §6.1/6.2 cut is the launch bar.
2. **Pricing** — negotiated per client, no published tiers at MVP.
3. **SLA** — none committed at MVP; baseline reliability practices (backups, TLS) apply regardless.
4. **Data residency** — India-hosted infrastructure.
5. **Launch vertical** — "General" preset first; second preset chosen when the first real client's business type is known.
6. **Module dependency enforcement** — warn-only, not hard-blocked, at MVP.
7. **Fork scope** — fork ERPNext only; Frappe Framework used stock from `frappe/frappe` upstream (no separate Frappe fork maintained).
