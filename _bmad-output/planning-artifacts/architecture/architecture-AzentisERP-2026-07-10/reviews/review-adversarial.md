---
name: 'AzentisERP'
type: review
subtype: adversarial
target: ARCHITECTURE-SPINE.md
purpose: 'Find pairs of spine-compliant units that build incompatibly with each other'
created: '2026-07-10'
---

# Adversarial Review — AzentisERP Architecture Spine

**Target:** `ARCHITECTURE-SPINE.md` (architecture-AzentisERP-2026-07-10)
**Sources read:** `prd.md`, `addendum.md` (prd-AzentisERP-2026-07-10)

## Method

For each AD, I asked: *could two competent builders (or two Claude Code agents working
independent stories) each satisfy this Rule to the letter, yet produce two units that
cannot be plugged together?* I looked specifically for clashing data shapes, dual owners
of one entity/state, conflicting mutation paths, Rule-text ambiguity, and FRs the
Capability→Architecture Map fails to route to a real governing AD. Findings below are
ordered by severity/build-blocking risk. Scope note: this is a solo, 1-month MVP — I did
not flag anything that is a legitimately-deferred v1.1/v2 item per PRD §6.2/Deferred.

## Verdict: **FAIL** (spine is strong overall, but ships with load-bearing ambiguities)

The spine's design paradigm and most ADs (AD-1, AD-5, AD-7, AD-8, AD-9, AD-10) are tight
and unambiguous. But five holes are real "build it twice, get two incompatible builds"
traps — three of them (Findings 1, 2, 3) are severe enough that a solo AI-assisted build
running Epics in parallel/sequence without a human catching the seam would very likely
produce silently-broken tenant branding or module toggling. This needs one more pass on
the spine (a handful of added sentences, not a rewrite) before it's safe to hand to
Epics/Stories.

---

## Finding 1 (Severity: High) — `custom_domain` vs. site-name identity is self-contradictory

**The conflict, in the spine's own words:**

- Consistency Conventions: *"Site name == tenant's domain exactly (Frappe DNS-multitenancy
  requirement — **no aliasing**)."*
- FR-7 (routed to AD-2 by the Capability Map): Tenant Settings holds a `custom_domain`
  field, editable independent of the site's name.
- PRD UJ-1 edge case (which the spine must still support — it's not in Deferred): *"Domain/DNS
  isn't yet pointed at the server — provisioning still succeeds against the
  subdomain/localhost pattern, and Ajit reconfigures DNS separately **without redoing the
  site setup**."*

These three statements cannot all be true simultaneously in stock Frappe. Frappe routes
purely by the literal site folder/name matching the request `Host` header. Making a
tenant's *real* domain (e.g. `clientshop.com`) resolve to a site originally created as
`clientshop.ourplatform.com` requires either (a) `bench rename-site` (destructive,
functionally *is* "redoing the site setup," contradicting UJ-1), or (b) Frappe's own
site-alias mechanism (`bench setup add-domain` / `currentsite`-style multi-domain
routing) — which is literally aliasing, contradicting the Consistency Convention's "no
aliasing" rule verbatim.

**Two independently-spine-compliant builds:**

- **Builder A** (owns FR-4–FR-6 provisioning, reads the Consistency Convention literally):
  treats `custom_domain` as a *display-only* field. Site name is the sole routing
  identity, set once at `bench new-site`, never aliased. If a tenant's domain changes,
  A's system has no defined path for it short of a manual `rename-site` (which A's own
  rule forbids treating as normal, so in practice: unsupported).
- **Builder B** (owns FR-7/FR-8 Tenant Settings + UJ-1's edge case, reads FR-7's field
  list + the PRD journey literally): wires a Tenant Settings `on_update` hook that calls
  Frappe's domain-alias mechanism whenever `custom_domain` changes, so the tenant's real
  domain routes to the existing site without recreating it — satisfying UJ-1, but
  directly violating "no aliasing."

Ship both stories and you get: either a `custom_domain` field that silently does nothing
(A wins) while support tickets ask "why doesn't my domain work," or a routing layer that
quietly grows site aliases the spine explicitly disallowed (B wins) — and whichever
Epic gets built second will look at the other's code and reasonably assume it's already
wrong, not realize the spine itself never picked a lane.

**Fix:** Add one sentence to AD-2 or a new short AD: state explicitly whether
`custom_domain` is (a) purely a display/branding label distinct from the site's routing
identity (and rename `custom_domain` in FR-7's field list accordingly so it doesn't imply
routing), or (b) the routing identity, in which case the "no aliasing" convention needs a
carve-out for the documented Frappe domain-alias path and UJ-1's edge case needs an
explicit mechanic (e.g., "site is always created under the internal subdomain pattern;
`custom_domain`, when set, is added via `bench setup add-domain` — this is the one
exception to 'no aliasing' and is the only supported domain-change path").

---

## Finding 2 (Severity: High) — `enabled_modules` has no agreed field shape

**The conflict:** The spine describes `enabled_modules` three different ways in three
places, none of them a concrete Frappe fieldtype:

- ER diagram: `list enabled_modules` (abstract "list").
- Addendum (authoritative field list, FR-7/FR-8): `enabled_modules (table/multi-select)` —
  itself two different real Frappe fieldtypes (`Table MultiSelect`, which is child rows
  against a linked doctype, vs. `MultiSelect`/plain multi-value widget, which is usually
  backed by a delimited string) named as if interchangeable.
- AD-5: preset application "copies its module list into the new Tenant Settings record as
  a snapshot — not a live foreign key," which reads naturally as *not* a `Link`/`Table
  MultiSelect` against Module Preset (that would risk looking like a live FK) but doesn't
  rule it out either, since child-table rows copied by value are also "not a live FK."

**Two independently-spine-compliant builds:**

- **Builder A** (owns FR-7, Tenant Settings DocType creation): picks a `Table MultiSelect`
  child table (idiomatic Frappe, matches "list" in the ER diagram, each row an object).
  Every reader must do `[d.module_name for d in doc.enabled_modules]`.
- **Builder B** (owns FR-9/FR-10, the sidebar-filter hook + AD-6 dependency validator):
  builds against a flat `Small Text`/JSON field (simpler to snapshot-copy per AD-5,
  simpler to `json.loads` in a hook), reading/writing `json.loads(doc.enabled_modules)`.

Both stories individually satisfy AD-2 ("holds... `enabled_modules`"), AD-4 (sidebar hook
reads it), AD-5 (snapshot-copy semantics), AD-6 (one validation function reads it) — but
A's DocType definition and B's hook/validator code are not interoperable. This is exactly
the kind of seam that two parallel Claude Code stories (one "build Tenant Settings
DocType," one "build the sidebar filter hook") would each pass their own acceptance
criteria on and only fail at integration.

**Fix:** Pin the exact Frappe fieldtype for `enabled_modules` in the spine (recommend:
`Table MultiSelect` against a lightweight child doctype, since AD-6's dependency map and
AD-5's snapshot-copy both become simpler with real rows), and state it once so both the
DocType-authoring story and the hook/validator story build against the same shape.

---

## Finding 3 (Severity: High) — AD-2's "cached accessor" contradicts AD-3's "reads live on every request" for the same read path

**The conflict, in the spine's own words:**

- AD-2: *"Every read path (branding injection, sidebar filtering) goes through **one
  cached accessor function** — never a scattered `frappe.get_single("Tenant Settings")`
  call at each call site."* Branding injection is explicitly named as a read path this
  rule governs.
- AD-3 (governs the same branding injection, FR-8): *"injected via a page-load hook that
  **reads Tenant Settings live on every request**. No per-tenant compiled asset file is
  ever generated."*

AD-2 mandates a cache; AD-3, read literally, mandates no staleness at all ("live... every
request"). AD-3's own "Prevents" clause is about compiled *assets*, not about caching a
DB read — so the charitable reading is "live" ≠ "uncached," it just means "not baked into
a build step." But nothing in the spine states that reconciliation; a literal-minded
builder implementing AD-3 has textual grounds to bypass the accessor entirely.

**Two independently-spine-compliant builds:**

- **Builder A** (implements FR-8 branding injection off AD-3's literal text): page-load
  hook calls `frappe.get_single("Tenant Settings")` directly every request — "live," no
  cache — which directly violates AD-2's "never a scattered `frappe.get_single()` call at
  each call site" for that exact read path.
- **Builder B** (implements the same feature off AD-2's literal text): routes through a
  cached accessor (e.g., `frappe.cache()` with a TTL, or an in-process memo invalidated on
  `Tenant Settings.on_update`) — compliant with AD-2, but now a tenant's color change is
  not guaranteed reflected on "next page load" the way FR-8's testable consequence
  requires, unless the invalidation is wired correctly.

If these are built as two separate stories (or even just two passes by the same agent
weeks apart), you get either a rule violation (A) or a cache-invalidation bug that
silently breaks FR-8's own explicit test ("changing color is visibly reflected on next
page load, no restart") if the TTL/invalidation isn't perfectly correct (B). Nothing in
the spine specifies invalidation strategy (TTL vs. explicit clear-on-save), so B's
"cached accessor" is itself underspecified enough that two builders could give it
different staleness windows.

**Fix:** Collapse to one rule: "the accessor function is called on every request (no
compiled artifact) but is cheap because it goes through `frappe.cache()`, explicitly
invalidated in `Tenant Settings.on_update`/`on_change` — never a TTL-only cache." State
this once in AD-2 or AD-3 (not both, worded differently), and delete the "live on every
request" phrasing from AD-3 or annotate it as "live" = "hook runs every request," not
"uncached."

---

## Finding 4 (Severity: Medium) — AD-6's "the same function" doesn't say where it lives or what shape the dependency map takes

AD-6's rule: *"One dependency map (data: `{module: [required_modules]}`) and one
validation function are the only path deciding warn conditions. Both the preset-apply
flow and the manual Tenant Settings toggle call the same function."*

This correctly rules out *duplicated logic*, but doesn't say:
- **Where the function lives** (a namespace not covered by the Layer→namespace table,
  which only lists `our_brand/commands/*` for provisioning and
  `our_brand/{doctype,hooks.py,public,templates}` for runtime — a function reachable from
  *both* the CLI-only provisioning pipeline (AD-8: "not a request-cycle concern") and a
  desk-UI manual toggle (a request-cycle concern) needs to live somewhere shared that
  no existing namespace row names).
- **What shape the dependency map is** — "data" per AD-5's philosophy could mean a
  DocType (edit via desk UI, matching the Flexibility NFR's spirit and AD-5's own
  precedent) or a static Python dict shipped in the app (also arguably "data," and is
  literally what AD-6's own `{module: [required_modules]}` notation looks like).

**Two independently-spine-compliant builds:** a "preset-apply" story and a "manual
toggle" story, built as separate Epics, could each independently write *their own*
compliant "the one validation function" — each satisfies AD-6 in isolation ("I call the
one function — the one I just wrote") while the two Epics never actually share code. This
is compounded by a related gap: the spine never enumerates the actual ~12-13 canonical
ERPNext Module Def strings its own Consistency Convention insists on using ("canonical
ERPNext Module Def string, never a locally invented alias") — the PRD's FR-9 prose list
("CRM, Sales, Purchasing, Accounting, HR, Inventory...") does not match ERPNext's real
Module Def names (`Selling`, `Buying`, `Accounts`, `Stock`, etc.). Two builders picking
their own "canonical" strings independently for Module Preset seed data vs. the
sidebar-filter hook's comparison logic can silently disagree, causing modules that never
hide/show correctly for any tenant.

**Fix:** Add a namespace row (e.g. `our_brand/our_brand/utils/module_rules.py`) explicitly
named as the one shared location for both the dependency map and its validation function,
importable from both `commands/provision.py` and DocType hook code. Separately, add a
short fixture/table to the spine (or the first Module Preset migration) pinning the exact
canonical Module Def string for each of the ~12 catalog areas.

---

## Finding 5 (Severity: Medium) — Capability Map misroutes FR-12 and FR-14; TLS-issuance ownership is genuinely undecided

The Capability → Architecture Map row for FR-12–FR-14 cites **AD-9** as a governing AD.
AD-9's actual Rule is entirely about the staging site living on the production bench — it
says nothing about TLS or firewall/SSH. AD-10 (the only other AD cited for this row)
covers backups only (FR-13). **FR-12 (TLS provisioning/renewal) and FR-14 (network access
control) have no governing AD at all**, despite the map implying otherwise.

This isn't just a documentation nit — it leaves a real build ambiguity. FR-11 promises
"one operator-triggered action" completing onboarding in under 10 minutes (SM-2), and
FR-12 promises TLS is provisioned "automatically" per tenant domain. The addendum lists
`bench setup lets-encrypt {site_name}` as a **separate, later, manually-run step**, not
part of `provision_client.sh`'s automated step list. Nothing in the spine's AD-7 idempotent
step checklist ("site exists? apps installed? Tenant Settings created? admin set? welcome
email sent?") mentions a cert-issuance step either — but nothing rules it out.

**Two independently-spine-compliant builds:**

- **Builder A** (owns FR-11, reads AD-7's idempotent-pipeline pattern as the obvious home
  for "automatic" per FR-12): adds a `request_cert` step to `provision.py`'s
  state-check sequence, blocking onboarding completion on Let's Encrypt HTTP-01
  validation, which itself blocks on DNS propagation — directly risking the "under 10
  minutes" SM-2 metric on every onboarding where DNS isn't pre-pointed (UJ-1's own edge
  case).
- **Builder B** (owns FR-12/FR-14 as ops/infra, reads the map's "Lives in: Server-level...
  not app code" annotation and the addendum's separately-numbered deployment steps
  literally): treats TLS issuance as a manual post-onboarding runbook step the operator
  runs by hand, entirely outside `provision.py` — meaning newly onboarded tenants are live
  on plain HTTP until the operator remembers the follow-up step, with no idempotent-pipeline
  tracking of whether it's been done (AD-7's resumability guarantee doesn't cover it).

Both readings are individually defensible from the spine text; they produce two different
completion-semantics for "onboarding is done" and two different provisioning-script
scopes that can't be merged without a rewrite of one side.

**Fix:** Correct the Capability Map row (FR-12/FR-14 shouldn't cite AD-9). Then explicitly
decide and state: is cert issuance a step inside AD-7's idempotent pipeline (recommended,
since AD-7 already exists to handle exactly this kind of "step can fail, must resume"
problem — but then SM-2's "under 10 minutes" needs a caveat for DNS-not-ready cases, matching
UJ-1's edge case), or is it explicitly out of the pipeline as a documented separate ops
step (in which case say so, and drop the word "automatically" from how FR-12 is described
in any builder-facing doc, or clarify it means "automated via certbot's renewal timer,
not via the onboarding pipeline").

---

## Finding 6 (Severity: Low) — possible double welcome-email owner

FR-11 / AD-7's step checklist explicitly includes "welcome email sent?" as a step the
provisioning pipeline owns and can resume. FR-3 requires branded transactional email
(including, presumably, whatever "welcome" email Frappe's own user-creation flow sends
when an admin User is created with `send_welcome_email` semantics — the addendum's source
tree even reserves `our_brand/templates/emails/` for this).

A builder implementing FR-11 literally (provisioning script explicitly calls
`frappe.sendmail(...)` with its own welcome template) and a builder implementing FR-3
literally (overrides Frappe's built-in new-user welcome-email template so it's branded
automatically whenever a User is created) can each be individually correct and yet, if
both fire for the same provisioning run and neither suppresses the other
(`send_welcome_email=0` on the admin User's `insert()` call is easy to forget), the client
receives two welcome emails — worst case, one branded and one not, directly undermining
SM-3 ("100% of tenant-facing surfaces... show zero Frappe/ERPNext branding").

**Fix:** One sentence in AD-7 or the FR-11 mapping: "the admin User is created with
`send_welcome_email` suppressed; the provisioning pipeline's own step sends the one
branded welcome email via the `our_brand` template." Low cost to state now, easy to
silently get wrong later.

---

## Summary Table

| # | Sev | The two units | What each reads literally | Why they collide |
|---|-----|----------------|----------------------------|-------------------|
| 1 | High | Provisioning/site-identity story vs. Tenant Settings `custom_domain` story | Consistency Convention "no aliasing" vs. FR-7 field + UJ-1 edge case | Spine self-contradicts on whether domain routing ever changes post-provisioning |
| 2 | High | Tenant Settings DocType story vs. sidebar-filter/dependency-validator story | ER diagram "list" / addendum "table/multi-select" | No pinned Frappe fieldtype for `enabled_modules` — readers and writer disagree on shape |
| 3 | High | Branding-injection implementation (AD-3-first reading) vs. (AD-2-first reading) | "reads... live on every request" vs. "one cached accessor function" | Direct rule-text tension on caching for the same read path |
| 4 | Medium | Preset-apply epic vs. manual-toggle epic | AD-6 "the same function," no namespace/shape given | Each epic can independently author its own compliant "the one function" |
| 5 | Medium | Provisioning-pipeline TLS step vs. manual ops-runbook TLS step | AD-7 idempotent pipeline vs. addendum's separate manual step; Map cites unrelated AD-9 | No AD actually governs FR-12/FR-14; two valid but incompatible provisioning scopes |
| 6 | Low | Provisioning's explicit sendmail vs. FR-3's built-in-template override | AD-7 "welcome email sent?" step vs. FR-3 branded transactional email | Risk of duplicate/unbranded welcome email if neither suppresses the other |

## What's *not* flagged (working as intended)

AD-1 (customization boundary), AD-5 (preset-as-data), AD-7/AD-8 (provisioning pipeline
shape and its SSH-only, no-hosted-API boundary), AD-9 (staging-on-same-bench), and AD-10
(backup mechanism/region) are all unambiguous enough that two independent builders would
converge on the same implementation. The Deferred section's cuts (full RBAC enforcement,
remote onboarding API, multi-server, hard-block dependencies, monitoring stack, automated
staged-update tooling, final brand name, backup vendor specifics, v16 migration) are all
appropriately scoped out for a solo 1-month MVP and are not re-flagged here.
