# Sprint Change Proposal — Desk UI Visual Theming (2026-07-12)

## 1. Issue Summary

The user requested a full modern-SaaS visual redesign of AzentisERP's entire ERPNext desk UI — navigation, dashboards, cards, tables, forms, buttons, empty/loading states, notifications, search, micro-interactions — across every module (CRM, Accounting, Buying, Selling, Manufacturing, Projects, Support, Users, Website, Reports, Settings), styled after Linear/Attio/Notion/Vercel/Stripe/HubSpot/Framer/Raycast, while preserving all business logic and backend APIs unchanged.

This was flagged as a scope conflict rather than implemented directly, because it contradicts two decisions already finalized earlier in this same project:

1. **PRD §5 Non-Goals** (founding constraint): *"AzentisERP will not modify Frappe or ERPNext core source for any customization — everything ships through the Branding App, hooks, Custom Fields, and Custom DocTypes."*
2. **DESIGN.md**'s own Do's/Don'ts table: *"Keep the glass/mesh/motion treatment to login + splash only"* / *"Don't extend glass, blur, or the animated mesh into any post-login desk screen."* The finalized design system deliberately scoped hero-surface treatment (login, splash) plus one flat navbar accent, leaving the inherited desk UI as stock ERPNext.
3. **Architecture AD-1**: Frappe Framework and ERPNext are pinned, unforked, read-only upstream dependencies, never modified.

No screenshot was attached despite being referenced in the request.

The user was asked to choose between (a) revising the design system/architecture and re-planning properly, (b) narrowing the request to something achievable within current constraints, or (c) proceeding with a full re-skin accepting it requires forking core and a much larger timeline. They chose (a).

## 2. Impact Analysis

**Epic Impact:**
- Epics 1-3 (all implemented, reviewed) are unaffected — none of their work touched desk UI beyond a single navbar accent color, so nothing requires rollback.
- Epics 4-5 (not started) are unaffected in their own scope, but Epic 5's premise (customizations must survive upstream Frappe/ERPNext updates) becomes higher-stakes if a large new CSS/JS surface targets desk-wide DOM structure that isn't a stable public API.
- A **new Epic 6** is added to hold this work, rather than folding it into an existing epic — the scope, prerequisites, and constraints are distinct enough to warrant its own slot.

**Artifact Conflicts:**
- **PRD**: needed a new functional requirement (FR-17) with an explicit non-goal clause, plus a Non-Goals amendment and an Out-of-Scope-for-MVP entry.
- **Architecture**: needed a new architecture decision (AD-12) establishing the CSS/JS-theming-vs-core-source-modification boundary, with an explicit cross-reference to Epic 5's upstream-update verification.
- **UX (DESIGN.md)**: did not need rewriting — its hero-surfaces-only scope is complete and remains valid. Needed only a scope-boundary note pointing to a future, separate UX session for the new work.
- **Epics.md**: needed a new Epic 6 entry, deliberately left as a scope/constraints placeholder rather than fully-written stories, since no design tokens exist yet for this surface.

**Technical Impact:** None yet — this proposal is planning-only. No code was touched. Epic 3's code review (running in parallel, unrelated to this change) was explicitly protected from collision by name (`module_rules.py`, `hooks.py`, `install.py`, `azentis/doctype/` were flagged as off-limits during this session pending that review's own resolution).

## 3. Recommended Approach

**Hybrid: Direct Adjustment (new epic, scoped subset) + MVP Review (explicit deferral).**

The full request as originally written is not achievable within the project's existing constraints (no core-source modification) without either forking Frappe/ERPNext (explicitly ruled out in the PRD from the start) or extensive client-side JS monkey-patching of Frappe's hard-coded list/table/kanban/search view classes (technically not "source modification," but fragile against upstream updates and never evaluated for risk).

What *is* achievable without violating existing constraints — global CSS/JS theming of colors/typography/spacing/iconography, plus Frappe's native Workspace/dashboard-widget system (itself a data-driven customization surface) — is real and worth pursuing, but is:
- Not part of the original MVP's success criteria (FR-1 through FR-16 don't include it),
- Not something to improvise inline in a change-management session — it needs its own dedicated UX design pass, same as the hero-surfaces work did,
- Appropriately deferred to v1.1+ given the project's 1-month solo-MVP framing, so Epics 1-5 (which the MVP's actual success metrics depend on) aren't put at risk of timeline slippage.

**Effort estimate:** High (full UX session + potentially thousands of lines of CSS/JS across every screen type + new upstream-fragility risk to manage). **Risk:** Medium-High if pursued aggressively (client-side monkey-patching), Low-Medium if scoped to the CSS/JS-theming-only boundary AD-12 establishes.

## 4. Detailed Change Proposals

All four applied as approved (Incremental review, each individually confirmed):

1. **PRD** (`prds/prd-AzentisERP-2026-07-10/prd.md`): new §4.8 + FR-17 (with explicit non-goal clause), Non-Goals amendment, §6.2 Out-of-Scope entry.
2. **Architecture** (`architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md`): new AD-12, inserted after AD-11.
3. **UX** (`ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md`): scope-boundary note added after the title, no other changes — hero-surfaces work stays `status: final` and untouched.
4. **Epics** (`epics.md`): new Epic 6 entry (scope/constraints placeholder, no stories yet), appended after Epic 5.

## 5. Implementation Handoff

**Scope classification: Major** — this is new product-quality investment requiring a full design pass, not a direct-implementation or backlog-reorg change.

**Handoff:**
- **Next real step**: a dedicated `bmad-ux` session (Update mode) to actually design Epic 6's desk-wide theming tokens and screens — this proposal deliberately does not invent them.
- **After that**: `bmad-create-epics-and-stories` (or a direct epics.md edit) to flesh out Epic 6's real stories against the resulting DESIGN.md tokens.
- **Not yet**: no Developer-agent implementation should start on Epic 6 until the UX session produces real tokens — Epic 6's current entry is intentionally a placeholder.
- Epics 1-5 continue on their existing track, unaffected. Epic 3's code review (in progress at the time of this proposal) is a separate, unrelated thread to be resolved on its own terms.

## 6. Success Criteria

- PRD, Architecture, UX, and Epics all consistently reflect that Epic 6 exists, is deferred to v1.1+, is bounded by AD-12's no-core-source-modification rule, and requires a UX session before implementation stories are written.
- No existing Epic 1-5 work is disturbed or rolled back.
- The next person (or session) picking up Epic 6 has enough context in these four documents to not repeat this same scope-conflict conversation from scratch.
