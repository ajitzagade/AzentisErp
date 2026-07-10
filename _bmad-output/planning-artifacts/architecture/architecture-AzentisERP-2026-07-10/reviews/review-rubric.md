# Review: ARCHITECTURE-SPINE.md vs. Good-Spine Rubric

**Subject:** `_bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md`
**Driving PRD:** `_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md` + `addendum.md`
**Context applied:** solo, AI-assisted, 1-month MVP; appropriately-scoped MVP deferrals are expected and not penalized.

**Overall verdict: PASS WITH NOTES**

The spine is well-constructed overall: 10 ADs each name a real two-implementer divergence risk, tech versions are unusually well-cited (`[ASSUMPTION]` tags, verified floors), and the Deferred list is genuinely non-load-bearing. However, one finding is a real contradiction between an unlabeled "Consistency Convention" and both the PRD and Frappe's actual mechanics, and one PRD capability (TLS automation) is left structurally ungoverned despite being map-cited to unrelated ADs. Both should be fixed before Epics/Stories lock in behavior around them.

---

## 1. Fixes real divergence points for the level below — misses some

Strong coverage overall (branding isolation, Tenant Settings ownership, dynamic injection, module toggling boundary, presets-as-data, dependency-check seam, idempotent provisioning, staging topology, backup mechanism/region). Two gaps:

- **TLS/certificate issuance and renewal (FR-12) has no AD and is not a step in AD-7's provisioning sequence.** AD-7's rule enumerates the pipeline's checkable steps explicitly ("site exists? apps installed? Tenant Settings created? admin set? welcome email sent?") — TLS/cert issuance is absent from that list, and the Stack/Deployment diagram never names Let's Encrypt/certbot even though the addendum's mechanics doc does (`bench setup lets-encrypt {site}`). Two independently-built provisioning stories could diverge on whether cert issuance is an idempotent step inside `provision.py` (participating in AD-7's resume-safety guarantee) or a separate manual/cron step outside it — which changes failure/retry semantics for "is this tenant fully live." This is exactly the kind of thing AD-7 exists to pin down, and it doesn't.
- **Custom-domain attachment after initial site creation is unaddressed as a build step.** See Finding in §5/§6 below — this is also a provisioning-pipeline divergence risk, not just a documentation nit.

## 2. Every AD's Rule is enforceable and prevents its stated divergence — pass

All 10 ADs pair a concrete divergence with a rule that would visibly fail code review if violated (grep for edits outside `our_brand`, grep for scattered `frappe.get_single("Tenant Settings")` calls, grep for a second dependency-check function, etc.). No AD's rule is vague enough to permit the divergence it claims to prevent. No issues found here.

## 3. Nothing under "Deferred" is load-bearing/urgent — pass

Checked each of the 9 deferred items against MVP scope (PRD §6.1/§6.2, §10 Resolved Decisions):

- Full RBAC-level module enforcement, hard-block dependency enforcement, self-service onboarding API, multi-server/HA, automated staged-update tooling, formal monitoring, final brand name, backup vendor specifics, v16 migration — every one of these maps to an explicit PRD non-goal or §6.2 out-of-scope item, or is genuinely a one-time/operational (not architectural) decision. None would cause two independently-built units to diverge in a way that breaks integration. No issues found here.

## 4. Named tech is verified-current — pass (one phrasing overreach)

Verified against current documentation:
- Frappe v15: Python 3.11+, Node 18+, MariaDB 10.3.x floor — **confirmed accurate**.
- Frappe v16 (2026): Python 3.14+, Node 24+ — **confirmed accurate**; the spine's rationale for staying on v15 for MVP is sound and current, not stale.
- MariaDB 10.6+ as "safer floor" above the verified 10.3.x — reasonable, not a hallucination.
- Frappe's native S3-compatible backup mechanism (AD-10) — **confirmed real** (Frappe's `push_backup`/S3 Backup Settings feature), though reporting suggests it may have moved/changed in v16 — irrelevant here since the spine targets v15.

One overreach: AD-10 and the Stack table both describe `ap-south-1` (Mumbai) as **"Frappe's verified native default region."** This is not accurate — `ap-south-1` is an AWS region choice driven by the PRD's India-data-residency decision (§10.4), not a Frappe framework default; Frappe's backup feature has no "default region" concept at all (it takes whatever bucket/endpoint you configure). Low severity — the underlying decision (use an S3-compatible bucket in an Indian region) is still correct and PRD-aligned — but the attribution should be corrected to avoid implying Frappe endorses/defaults to that region.

## 5. Ratifies rather than contradicts the driving PRD — fail on one point, otherwise pass

Coverage of FR-1–FR-16 in the Capability → Architecture Map is complete (every FR appears). Cross-checked against PRD text; one direct contradiction found:

- **The "no aliasing" convention contradicts PRD UJ-1 and FR-7, and is not how Frappe actually works.** The Consistency Conventions table states: *"Site name == tenant's domain exactly (Frappe DNS-multitenancy requirement — no aliasing)."* But:
  - PRD UJ-1's stated edge case: *"Domain/DNS isn't yet pointed at the server — provisioning still succeeds against the subdomain/localhost pattern, and Ajit reconfigures DNS separately without redoing the site setup."* This requires a site created under one name (e.g., a subdomain) to later serve a different, final custom domain — i.e., exactly the aliasing the convention rules out.
  - FR-7 explicitly lists `custom_domain` as a Tenant Settings field, implying a tenant's addressable domain is not fixed to the site's creation-time name.
  - Frappe itself supports this natively via `bench setup add-domain <domain> --site <site>` (confirmed via Frappe docs/wiki), which attaches an additional domain to an existing site without renaming it — the framework does not require "no aliasing"; that's the opposite of its documented multi-domain support.
  
  As written, an implementer following the spine's convention literally would have to *recreate* the site under the final domain to honor "site name == domain, no aliasing," directly breaking UJ-1's "without redoing the site setup" requirement. This needs to be corrected — either drop "no aliasing" and add an explicit AD/step for `bench setup add-domain` as part of onboarding/post-onboarding, or clarify that `custom_domain` in Tenant Settings is purely informational/branding (e.g., for display or email links) and is *not* the DNS-routing key — but that reading needs to be stated, not left implicit, since as currently worded it reads as a hard rule that conflicts with the PRD.

No other FR-level contradictions found. Data residency (AD-10 ↔ PRD §10.4), warn-only dependency checks (AD-6 ↔ PRD SM-C2/OQ6), navigation-only module toggling (AD-4 ↔ FR-9's testable consequences), and the fork-scope decision (AD-1 diagram ↔ PRD §10.7 "Frappe unforked, ERPNext forked") are all correctly ratified.

## 6. Every structural dimension this altitude owns is decided/deferred/flagged — mostly pass, one silent dimension

The operational/environmental envelope is handled better than most drafts at this altitude: there's an explicit Deployment & environments diagram, a Stack table, a staging-topology AD (AD-9), a backup mechanism/region AD (AD-10), and network/access posture is at least named (FR-14, left as one-time server hardening — reasonable to leave undecided-by-AD since it's not a repeated per-story divergence risk).

One dimension is silently under-governed rather than explicitly decided or deferred:

- **TLS/certificate automation (FR-12)** appears in the Capability → Architecture Map mapped to "AD-9, AD-10" — but neither AD actually addresses certificates; AD-9 is about staging topology, AD-10 is about backups. This reads as "governed" when it isn't. It should either get its own AD (e.g., naming `bench setup lets-encrypt` as a per-site provisioning step folded into AD-7's idempotent sequence) or be explicitly added to the Deferred list with a rationale (e.g., "one-time per-tenant `certbot`/Let's Encrypt setup, not idempotent-pipeline-critical, verified manually at MVP") — either is fine, but the current silent mis-mapping is not.

Two smaller silent items, lower severity, worth a mention but not blocking given MVP scope:
- **Welcome-email transport (SMTP)** is referenced by FR-3/FR-11 but never named in Stack or an AD — not clearly load-bearing (likely inherited from Frappe's existing email queue/SMTP config), but two builders could diverge on whether it's a shared platform SMTP account or something else. Low risk; could be left implicit given it's inherited stock Frappe behavior, but a one-line note would remove ambiguity cheaply.
- **Test/QA strategy** is not mentioned anywhere in the spine. For a solo, 1-month AI-assisted MVP this is a defensible omission (not flagging as a required build-now item), but per rubric #6 a dimension left completely silent is worth a one-line acknowledgment (even just "manual verification against each FR's testable consequences; no automated test suite at MVP") so it reads as a decision rather than an oversight.

---

## Summary Table

| # | Rubric item | Verdict |
|---|---|---|
| 1 | Fixes real divergence points, misses none | Notes — TLS/cert automation and custom-domain attachment missing from AD-7's pipeline |
| 2 | Every AD's Rule enforceable & prevents its divergence | Pass |
| 3 | Nothing Deferred is load-bearing/urgent | Pass |
| 4 | Named tech verified-current | Pass — one minor phrasing overreach ("Frappe's verified native default region" for ap-south-1) |
| 5 | Ratifies rather than contradicts PRD | Fail on one point — "no aliasing" convention contradicts UJ-1/FR-7 and Frappe's actual `add-domain` mechanism |
| 6 | Every structural dimension decided/deferred/flagged | Notes — TLS ownership silently mis-mapped; SMTP and test strategy silent (low severity) |

## Recommended fixes (priority order)

1. Resolve the domain-aliasing contradiction (§5) — either adopt `bench setup add-domain` as the mechanism for attaching a tenant's final custom domain post-onboarding (and drop "no aliasing"), or explicitly redefine what `custom_domain` in Tenant Settings means if it's not the DNS-routing key.
2. Give TLS/certificate automation an explicit owner: fold into AD-7's idempotent step list, or add a dedicated AD, or move to Deferred with rationale.
3. Correct the "Frappe's verified native default region" phrasing for `ap-south-1` to attribute the choice to the PRD's data-residency decision, not to Frappe.
4. Optional/cheap: one line each on SMTP transport ownership and test/QA approach at MVP, to remove ambiguity for the Epics/Stories pass.
