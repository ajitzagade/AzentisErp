---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: ['_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md', '_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/addendum.md', '_bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md', '_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md', '_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/EXPERIENCE.md', '_bmad-output/planning-artifacts/epics.md']
---

# Implementation Readiness Assessment Report

**Date:** 2026-07-10
**Project:** AzentisERP

## Document Inventory

| Document | Path |
|---|---|
| PRD | `_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md` (+ `addendum.md`) |
| Architecture Spine | `_bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md` |
| UX Design Contract | `_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md` + `EXPERIENCE.md` |
| Epics & Stories | `_bmad-output/planning-artifacts/epics.md` (canonical; per-epic folder files under `epics/` are synced mirror copies, not used as assessment source) |

No true duplicates found. User confirmed `epics.md` as the authoritative epics/stories source.

## PRD Analysis

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

Total FRs: 16

### Non-Functional Requirements

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

Total NFRs: 10

### Additional Requirements

- Fork scope: ERPNext is forked under the org's GitHub account (`version-15` branch); Frappe Framework itself is deliberately NOT forked, used stock from `frappe/frappe` (PRD §10.7 resolved decision).
- MVP scope split (PRD §6): full Branding App + multi-tenancy + Tenant Settings + ≥1 module preset + baseline production hardening are IN scope; full preset catalog, monitoring/alerting dashboard, self-service admin UI, HA/multi-server, and formal update-automation tooling are explicitly OUT of MVP scope (deferred to v1.1/v2).
- Business constraints: India-first SMB target market, negotiated/case-by-case pricing (no fixed tier menu at MVP), no formal SLA at MVP, India-hosted infrastructure (data residency), solo/AI-assisted builder with a 1-month target timeline (PRD §10, all resolved decisions).
- Constraints and Guardrails (PRD, standing rules, not FR-numbered): prefer Custom Fields/Custom DocTypes via UI over code forks for client-specific needs; every upstream merge verified on staging before touching any tenant (duplicates NFR10, stated twice in PRD for emphasis).

### PRD Completeness Assessment

The PRD is complete and internally consistent for MVP scope. All 16 FRs are unambiguous, testable (each carries explicit "Consequences" in the source PRD), and traceable to a Glossary-defined vocabulary. All open items from the original draft (6 open questions plus the fork-scope question raised mid-session) were resolved with explicit, logged decisions in PRD §10 rather than left as live ambiguity — this is a stronger-than-typical starting position for a fast-path PRD. No gaps found between PRD scope and what Architecture/Epics later assumed.

## Epic Coverage Validation

### Coverage Matrix

Verified at the story level (each FR traced to a specific story's acceptance criteria, not just the epic-level coverage-map claim at the top of `epics.md`).

| FR | PRD Requirement (summary) | Epic Coverage | Status |
|---|---|---|---|
| FR1 | Platform-level brand override | Epic 1, Story 1.2 | ✓ Covered |
| FR2 | Visual theming (colors/login/splash) | Epic 1, Story 1.3 | ✓ Covered |
| FR3 | Branded transactional email | Epic 1, Story 1.4 | ✓ Covered |
| FR4 | Isolated per-tenant site | Epic 2, Story 2.2 | ✓ Covered |
| FR5 | DNS-based routing | Epic 2, Story 2.1 | ✓ Covered |
| FR6 | Repeatable provisioning script | Epic 4, Story 4.2 | ✓ Covered |
| FR7 | Tenant Settings record | Epic 1, Story 1.5 | ✓ Covered |
| FR8 | Dynamic per-tenant branding injection | Epic 1, Story 1.6 | ✓ Covered |
| FR9 | Per-tenant module enable/disable | Epic 3, Story 3.2 | ✓ Covered |
| FR10 | Business-type module presets | Epic 3, Story 3.4 | ✓ Covered |
| FR11 | One-action client onboarding | Epic 4, Story 4.2 | ✓ Covered |
| FR12 | TLS for every tenant domain | Epic 4, Story 4.3 | ✓ Covered |
| FR13 | Automated backups | Epic 5, Story 5.1 | ✓ Covered |
| FR14 | Network access control | Epic 5, Story 5.2 | ✓ Covered |
| FR15 | Customization isolation | Epic 5, Story 5.5 | ✓ Covered |
| FR16 | Staged rollout of upstream updates | Epic 5, Story 5.4 | ✓ Covered |

### Missing Requirements

None. All 16 FRs have at least one story-level AC reference.

### Coverage Statistics

- Total PRD FRs: 16
- FRs covered in epics: 16
- Coverage percentage: 100%
- FRs found in epics but not in PRD: none (epics were derived directly from the PRD's FR list, no extraneous FRs introduced)

## UX Alignment Assessment

### UX Document Status

Found. `ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md` + `EXPERIENCE.md`, both `status: final`, scoped to the branding/theming layer (login, splash, navbar accent, transactional email header).

### UX ↔ PRD Alignment

- Flow 1 in `EXPERIENCE.md` correctly mirrors PRD UJ-2 (Priya's first login) — verified consistent, no drift.
- Two UX-committed requirements have **no corresponding PRD FR**: (1) dark/light theme support, (2) mobile-first responsive design. Both were introduced directly by the user during the UX pass (session-native decisions, not derived from the PRD), so this isn't a PRD authoring gap — but the PRD's FR2 ("visual theming... via the Branding App's stylesheet") doesn't explicitly say "including dark/light and mobile," and neither does any other FR. Minor — these read as reasonable elaborations of FR2/FR8's intent, not contradictions — but worth a PM note since anyone reading the PRD alone would not know these are committed requirements.

### UX ↔ Architecture Alignment

No contradiction. Architecture Spine AD-3 ("tenant colors render as inline CSS custom properties, injected live on every request") was written *before* the UX pass, so it doesn't mention dark mode, motion, or mobile explicitly — but the mechanism it specifies fully supports what `DESIGN.md` later needed (CSS custom properties can carry light/dark/mobile variants without any architectural change). Compatible-but-silent, not misaligned.

### ⚠️ UX ↔ Epics/Stories Alignment — CRITICAL GAP FOUND

This is the most significant finding in this assessment. The UX pass ran **after** Epic 1's stories were already written and approved, produced substantial new committed decisions (`status: final` in both spines), and the workflow correctly returned to finish Epics 2–5 afterward — but **Epic 1's already-written stories (1.2, 1.3, 1.5, 1.6) were never revised** to incorporate what the UX pass had just finalized. Searching `epics.md` for the UX spines' key terms confirms this directly: zero matches for "dark," "prefers-color-scheme," "mobile," "responsive," "prefers-reduced-motion," or "backdrop-filter" anywhere in the document. "Splash" appears only in Story 1.3's narrative intro sentence, never in an actual acceptance criterion. "login_background" appears only as a field name in Story 1.5's schema list, with its override behavior (a `status: final` decision in `DESIGN.md`) never tested anywhere.

**Specific gaps, each a `DESIGN.md`/`EXPERIENCE.md` `final` decision with no story-level AC:**

1. **Dark/light theme switching** (`prefers-color-scheme`) — no AC anywhere tests that the login/splash surfaces render the correct theme tokens automatically.
2. **Mobile responsive behavior** — fluid card width, 16px input font-size (iOS zoom prevention), 44/48px touch targets, `dvh` viewport unit, `env(safe-area-inset-*)` — none of this is tested. This is a real risk given Flow 1 (the PRD's own primary journey) is explicitly a phone login.
3. **Reduced-motion support** (`prefers-reduced-motion`) — a hard accessibility requirement in `EXPERIENCE.md`, untested.
4. **`backdrop-filter` fallback** — the glass card's graceful degradation to a near-opaque surface on unsupported browsers, untested.
5. **Contrast-safe button text** — `DESIGN.md`'s server-computed `on-primary` color (never hardcoded white) is a real correctness rule with no story enforcing it.
6. **`login_background` override behavior** — the field exists in Story 1.5's schema, but the "image replaces the mesh when set" behavior (a real product decision) is never tested.
7. **Splash screen as its own surface** — Story 1.3's *narrative* mentions the splash screen, but its acceptance criteria only test the login page. There is currently no AC anywhere that the splash screen exists, renders, or auto-dismisses correctly.

**Recommendation:** Stories 1.2, 1.3, 1.5, and 1.6 need to be amended with new acceptance criteria (or one new story added specifically for the splash screen) before Epic 1 is implementation-ready. This should happen via `bmad-create-epics-and-stories`' Update flow, or as a direct edit, before Sprint Planning — not deferred, since Epic 1 is the first epic scheduled for implementation.

### Warnings

- The two PRD-uncaptured UX requirements (dark mode, mobile-first) should be added to the PRD's FR2/FR8 text or logged as an explicit PRD amendment, so the PRD remains the accurate single source of truth for what's being built.

## Epic Quality Review

Applying create-epics-and-stories standards with fresh, adversarial scrutiny — not re-confirming the workflow's own self-check, actively hunting for what it might have missed.

### Epic Structure Validation

**User Value Focus** — All 5 epic titles/goals are user- or operator-centric outcomes, not technical milestones. No epic is itself a disguised technical layer (no "Database Setup" or "API Development" epic exists).

**Epic Independence** — Re-traced every cross-epic reference independently: Epic 2 → Story 1.5 (backward), Epic 3 → Story 1.5 + Epic 1's fail-open convention (backward), Epic 4 → Epics 1–3, Story 3.4, Story 1.4 (backward), Epic 5 → Story 4.1 (backward). Zero forward references found. One notable clean pattern: Story 1.5's AC explicitly states `enabled_modules` is "deliberately NOT added yet — that's Epic 3's concern" — this *names* a later epic but only to declare a scope boundary, not as a functional dependency; Story 1.5 doesn't require Epic 3 to function. Correctly not a violation.

### Story Quality Assessment

**Story-level "technical milestone" check:** Two stories read as infrastructure work with user-story framing bolted on rather than genuine end-user value:

- **Story 1.1** ("Fork ERPNext and Bootstrap the Base Platform") — this is explicitly sanctioned: it matches this skill's own starter-template pattern (§5A: "Epic 1 Story 1 must be 'Set up initial project from starter template'... cloning, dependencies, initial configuration"). Fork = clone, `bench init`/`get-app` = dependencies, `new-site`/`install-app` = initial config. Not a violation.
- **Story 4.1** ("Stand Up Production Server Infrastructure") — 🟡 **Minor.** No equivalent exemption covers this one. Its "So that" clause reads "so that Epic 4's onboarding pipeline has something real to provision clients onto" — internal epic mechanics, not end-user value. Structurally this is fine (a necessary technical foundation inside a value-delivering epic, same shape as Story 1.1's justified case), but the framing itself is weaker than the rest of the document's stories. Recommend rewording the "So that" to something like "so that a real client can actually be onboarded onto working infrastructure" — cosmetic, not blocking.

**Acceptance Criteria depth:** 🟡 **Minor.** Two stories are thin (single AC, no negative-path coverage):
- **Story 5.2** (Restrict Network Access) — only tests the positive case (80/443 open). No AC verifies the negative case (other ports actually rejected, unauthorized SSH actually denied) — worth adding given this is a security-relevant control, not just a convenience feature.
- **Story 3.3** (Module Preset Data Model) — single AC, but acceptable given it's a minimal schema story tightly paired with Story 3.4's seeding.

All other 21 stories have appropriately specific, testable, multi-scenario ACs (happy path + at least one edge/failure case each) — this is above-average AC quality for the stage.

### Dependency Analysis

**Within-epic sequencing** — Re-verified all 5 epics story-by-story: 1.1→1.2→1.3→1.4→1.5→1.6, 2.1/2.2/2.3 (independent of each other), 3.1→3.2→3.3→3.4→3.5, 4.1→4.2→4.3→4.4, 5.1/5.2/5.3 (independent) →5.4→5.5. No story references a later story's output as a precondition anywhere.

**Database/Entity creation timing** — Confirmed "create only when needed": Tenant Settings created branding-only (Story 1.5), extended with `enabled_modules` only in Story 3.1 when Epic 3 needs it; Module Preset DocType created only in Story 3.3 when needed. No upfront over-creation found.

### Special Implementation Checks

- **Starter template pattern** — satisfied correctly by Story 1.1 (see above).
- **Greenfield vs. brownfield** — this project is a hybrid: greenfield for the Branding App layer, brownfield-adjacent for the ERPNext/Frappe foundation being forked. No CI/CD pipeline story exists — **not a new gap**: this matches an already-documented, deliberate deferral (Architecture Spine's Deferred section: "Formal test/QA strategy... acceptable to defer for a solo 1-month MVP").

### Best Practices Compliance Checklist

| Epic | User value | Independent | Sized right | No forward deps | DB timing | Clear ACs | FR traceable |
|---|---|---|---|---|---|---|---|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ (Story 4.1 framing noted above) | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (Story 5.2 thin, noted above) | ✓ |

### Findings by Severity

**🔴 Critical Violations:** None found at the epic/story structural level. (The UX↔Epics gap from the previous section is the assessment's one critical finding overall, but it's a cross-document alignment issue, not a structural epics-and-stories violation.)

**🟠 Major Issues:** None found in this step.

**🟡 Minor Concerns:**
1. Story 4.1's "So that" clause leans on internal mechanics rather than end-user language — cosmetic reword recommended, not blocking.
2. Story 5.2 lacks a negative-path AC for a security-relevant control — recommend adding one before Epic 5 implementation, not blocking for Epic 1.

## Summary and Recommendations

### Overall Readiness Status

**NEEDS WORK** (targeted, not sweeping) — the foundation across all four documents is genuinely strong: 100% FR coverage at the story level, zero structural violations (no forward dependencies, no technical-milestone epics, correct database-timing discipline, clean epic independence), and a PRD with every prior open question explicitly resolved rather than left ambiguous. This is not a "start over" or "add more planning" verdict. But there is one concrete, fixable gap that should close before implementation starts, because it affects the very first epic scheduled for development.

### Critical Issues Requiring Immediate Action

1. **UX ↔ Epics/Stories misalignment (Epic 1).** The UX pass (`DESIGN.md`/`EXPERIENCE.md`, both `status: final`) ran after Epic 1's stories were already written, and produced seven concrete, committed decisions that were never threaded back into Epic 1's acceptance criteria: dark/light theme switching, mobile responsive behavior (fluid width, 16px input font-size, touch targets, `dvh`, safe-area insets), reduced-motion support, `backdrop-filter` fallback, server-computed contrast-safe button text, the `login_background` override behavior, and the splash screen as a tested surface (currently only mentioned in Story 1.3's narrative, never in its ACs). None of this is a design problem — the spines are well-decided — it's a threading problem: real requirements that exist in a finalized source document but aren't yet enforceable via any story's acceptance criteria.

### Recommended Next Steps

1. **Amend Epic 1's stories before Sprint Planning.** Specifically: add dark/light-theme, motion, and contrast ACs to Story 1.3 (Visual Theming); add mobile-responsive ACs to Story 1.3 and/or 1.6; add the `login_background` override behavior as an AC to Story 1.5 or 1.6; add explicit splash-screen ACs to Story 1.3 (or split it into a dedicated splash story, given it currently carries two surfaces' worth of narrative but only one surface's worth of ACs). This can go through `bmad-create-epics-and-stories`' Update flow, or as a direct, reviewed edit — either is fine given the changes are additive (new ACs on existing stories), not structural.
2. **Log the two UX-only requirements (dark mode, mobile-first) back into the PRD** — a short amendment to FR2/FR8's text, or a new FR, so the PRD remains the accurate source of truth rather than something only `DESIGN.md` knows about.
3. **Cosmetic, non-blocking, whenever convenient:** reword Story 4.1's "So that" clause toward end-user value; add a negative-path AC to Story 5.2 before Epic 5 is implemented (not urgent — Epic 5 is last in the build order).

### Final Note

This assessment identified 1 critical issue (7 sub-items, all in one place — Epic 1's ACs), 2 minor structural concerns, and 2 documentation-completeness warnings, across the UX Alignment and Epic Quality Review categories. FR coverage, epic independence, dependency ordering, and database-creation discipline all passed clean. Recommend closing the critical issue (Epic 1's AC amendments) before starting Sprint Planning — it's scoped narrowly enough to resolve in one focused pass, not a reason to revisit the overall plan.

## Amendments Applied — 2026-07-10

All recommended actions from this assessment were applied the same day:

1. **Epic 1 amended.** Story 1.3 expanded with dark/light theme, reduced-motion, `backdrop-filter` fallback, contrast-safe button text, mobile-responsive, and `login_background`-override acceptance criteria. New Story 1.4 added for the splash screen (previously named only in narrative text, never tested). Old Stories 1.4–1.6 renumbered to 1.5–1.7 accordingly; Story 1.7 gained an additional AC for `login_background`'s live-injection behavior. Epic 1 is now 7 stories (was 6). All cross-references elsewhere in `epics.md` (Epic 2 Story 2.3, Epic 3 Stories 3.1/3.2, Epic 4 Story 4.4) updated to point at the correct renumbered stories — verified via full-document grep, no stale references remain. `epics.md`'s UX Design Requirements section rewritten from "not applicable" to 6 explicit UX-DRs, each mapped to its covering story. Per-epic mirror files (`epics/epic-1-.../epic.md`, `epic-4-.../epic.md`, `epic-5-.../epic.md`) re-synced to match.
2. **PRD amended.** FR-2 and FR-8 in `prds/prd-AzentisERP-2026-07-10/prd.md` updated to explicitly capture dark/light theme, mobile-responsiveness, and `login_background` — previously only known to the UX spines.
3. **Cosmetic fixes applied.** Story 4.1's "So that" clause reworded toward end-user value; Story 5.2 gained a negative-path AC (other ports verified unresponsive, not just assumed from config).

Epic 1 is now implementation-ready with no known gaps against PRD, Architecture, or UX.
