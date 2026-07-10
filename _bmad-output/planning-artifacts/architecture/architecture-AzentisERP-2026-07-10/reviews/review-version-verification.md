# Version/Currency Verification Review — ARCHITECTURE-SPINE.md

**Reviewed file:** `_bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md`
**Review date:** 2026-07-10
**Method:** Independent web search/fetch against primary sources (Frappe/ERPNext official docs, GitHub wiki/source, MariaDB/Ubuntu/Node.js EOL trackers), targeting "as of 2026" currency. No claim below was taken from model training data without a corroborating live source.

**Overall verdict: PASS WITH NOTES**

The core framework/runtime version claims (Frappe v15 requirements, the existence and requirements of v16, DNS multitenancy mechanics, `bench setup production` topology) check out against live sources and were evidently researched, not just asserted. However, one architecturally-binding claim (AD-10's S3 backup default region) could not be corroborated by any primary source and appears to be an unverified/fabricated fact promoted to a design rule, and two infrastructure floor versions (MariaDB 10.6, Node 18) are already past their own upstream end-of-life as of today — a currency check the document doesn't appear to have run against *today's* date specifically. Details below.

---

## 1. Frappe Framework v15 requirements (Python 3.11+, Node 18+, MariaDB 10.3.x) — CONFIRMED ACCURATE

The spine states: *"Frappe Framework — `version-15` branch ... verified requires Python 3.11+, Node 18+, MariaDB 10.3.x minimum"* (Stack table, line 117).

Independent search of Frappe's own installation docs confirms: Python 3.11+, Node.js 18+, Redis 5, MariaDB 10.3.x / Postgres 9.5.x, yarn 1.12+, pip 20+, wkhtmltopdf 0.12.5 (patched Qt) — exact match.

- Source: [Installation — frappeframework.com/docs/v15](https://frappeframework.com/docs/v15/user/en/installation)
- Source: [Installation — docs.frappe.io/framework](https://docs.frappe.io/framework/user/en/installation)

**Verdict: matches live documentation. No issue.**

---

## 2. Frappe Framework v16 exists as of 2026, requires Python 3.14 / Node 24 — CONFIRMED ACCURATE

The spine's assumption footnote states v16 "exists as of 2026, requiring Python 3.14/Node 24."

Confirmed: Frappe v16 requires Python 3.14 and Node.js 24 (LTS recommended before building assets). Frappe v16 beta released Nov 15, 2025; stable/GA released **Dec 6, 2025** at Frappeverse Egypt — i.e., roughly 7 months before this document's creation date (2026-07-10), not a hypothetical/future release.

- Source: [Migrating to version 16 — frappe/frappe wiki](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)
- Source: [Frappe and Python 3.14 — Frappe Forum](https://discuss.frappe.io/t/frappe-and-python-3-14/159316)
- Source: [ERPNext Quick Install Script: v16 Support (Python 3.14 + Node 24) — Frappe Forum](https://discuss.frappe.io/t/erpnext-quick-install-script-v16-support-python-3-14-node-24/159244)
- Source: [ERPNext Version 16 — Features & Updates — frappe.io](https://frappe.io/erpnext/version-16)

**Verdict: numerically accurate. One nuance the document doesn't surface** (see §7 below): v16 is not "brand new/unproven" as the surrounding rationale implies — it has been GA for ~7 months and Frappe's own marketing already calls it "our most stable and secure version yet." This weakens (but doesn't invalidate) the stated rationale for staying on v15.

---

## 3. ERPNext v15 — CONFIRMED as current recommended stable at time of writing, with a caveat

The official `frappe/erpnext` GitHub wiki "Supported Versions" page (fetched live) shows:

| Version | EOL | Status |
|---|---|---|
| 14 | Jan 31, 2026 | Maintenance (nearly EOL) |
| 15 | End of 2027 | **Current/Latest Stable — recommended for production** |
| 16 | End of 2029 | Latest, forward-looking |

This directly supports the spine's choice of v15 as the safe MVP target — this claim *is* well-grounded.

- Source: [Supported Versions — frappe/erpnext wiki](https://github.com/frappe/erpnext/wiki/Supported-Versions)

**Caveat:** this conflicts somewhat with Frappe's own v16 marketing copy ("production-ready," "most stable ... yet") and third-party field guides already published (e.g. a June 2026 "field-tested" v15→v16 upgrade guide), suggesting real-world v16 adoption is ahead of what the wiki's conservative "current stable" label implies. Not a factual error in the spine, but the "documentation maturity" justification for deferring v16 is softer than the document presents it — worth a sentence acknowledging the tension rather than treating v16 as clearly immature.

- Source: [Upgrading ERPNext from V15 to V16: A Field-Tested Guide (June 2026)](https://codewithkarani.com/2026/06/04/upgrading-erpnext-from-version-15-to-version-16-a-field-tested-guide/)

---

## 4. MariaDB 10.6+ as the deployment floor — STALE, NOT VERIFIED AGAINST TODAY'S DATE

The spine states: *"MariaDB | 10.6+ (verified v15 floor is 10.3.x; 10.6+ used as the safer floor per original plan)"*.

**Finding: MariaDB Community Server 10.6 reached End of Life on July 6, 2026 — four days before this document's stated date (2026-07-10).** As of today, 10.6 receives no further security or bug fixes from the MariaDB Foundation. Recommending "10.6+" as a *floor* for a new MVP deployment starting today means the floor itself is already an unsupported version if taken literally as "10.6."

The current safer LTS floors as of today are MariaDB 10.11 (LTS, supported to Feb 2028) or 11.4 (LTS, supported to May 2029).

- Source: [MariaDB Server 10.6 Reaches End of Life on July 6th — mariadb.org](https://mariadb.org/mariadb-server-10-6-reaches-end-of-life-on-july-6th/)
- Source: [MariaDB Community Server 10.6 Is Reaching End of Life — mariadb.com](https://mariadb.com/resources/blog/mariadb-community-server-10-6-is-reaching-end-of-life-heres-what-to-do-next/)
- Source: [MariaDB End-of-Life Dates — endoflife.ai](https://endoflife.ai/article-mariadb-eol)

**This reads as a version pinned from training-data-era knowledge ("10.6 is a safe modern default") rather than checked against the live EOL calendar for 2026.** Recommend bumping the floor to 10.11 (matches Frappe v15's compatibility easily, since the framework floor is only 10.3.x) and noting this explicitly rather than leaving "10.6+ per original plan" unexamined.

---

## 5. Node.js 18+ — technically matches Frappe's documented floor, but the floor itself is EOL

Frappe v15's own docs do say "Node.js 18+," so the spine's citation is accurate as a *quote of the framework requirement* (§1 above). However, independently: **Node.js 18 reached end-of-life on April 30, 2025** — over a year before this document's date — and receives no security patches.

The spine doesn't distinguish "framework's documented floor" from "what you should actually deploy," and a reader could take "Node.js | 18+" at face value and provision Node 18. This wasn't flagged as a currency risk anywhere in the document.

- Source: [Node.js — End-Of-Life — nodejs.org](https://nodejs.org/en/about/eol)
- Source: [Node.js 18 End of Life Date — EOL Apr 30, 2025 — endoflife.ai](https://endoflife.ai/nodejs/18)

**Recommend:** state the deployable target as "Node.js 20 LTS or 22 LTS (satisfies Frappe v15's 18+ floor; Node 18 itself is EOL since April 2025 and should not be provisioned)."

---

## 6. Ubuntu 22.04+ — currently fine, not urgent

Ubuntu 22.04 LTS has standard support until April 2027 (current as of today), so "22.04+" is not wrong. Ubuntu 24.04 LTS (support to April 2029, ESM to 2034) would give more runway for a platform meant to run for years, but this is a reasonable, defensible choice, not a stale/incorrect one.

- Source: [Ubuntu End-of-Life Dates — endoflife.ai](https://endoflife.ai/ubuntu)

**Verdict: acceptable, minor optimization opportunity only.**

---

## 7. AD-10 — Backup default region "ap-south-1 (Mumbai)" — **UNVERIFIED / LIKELY INCORRECT, FLAG FOR CORRECTION**

This is the most significant finding. AD-10 states:

> "targeting an S3-compatible bucket in the `ap-south-1` (Mumbai) region — consistent with ... Frappe's own verified default region" ... `[ASSUMPTION: ... AWS S3 ap-south-1 is Frappe's verified default ...]`

This claim was **checked directly against primary sources and does not hold up**:

- **The official Frappe documentation page for this exact feature** (`docs.frappe.io/erpnext/aws_s3`, fetched directly) contains **no mention of any default region**. It instructs users to create an S3 bucket and configure IAM access, with no region default stated anywhere.
- **The Frappe framework source** (`frappe/utils/backups.py`, the module that implements backup creation) contains **no S3 or region logic at all** — S3 upload is a separate concern (S3 Backup Settings DocType / `push_backup` script), and nothing in the reviewed code path hardcodes `ap-south-1`.
- Multiple **GitHub issues against `frappe/frappe` and `frappe/erpnext`** show that the S3 backup region is a **required, user-supplied** `boto3` parameter, and that *omitting* it has historically caused connection errors (boto3's own SDK-level default is `us-east-1`, not `ap-south-1`) — the opposite of there being a Mumbai default baked into the mechanism.
- Web-search AI-overview summaries repeatedly asserted "backups default to ap-south-1 (Mumbai)" as a bare claim with no attributable source — this looks like a case of a plausible-sounding but unsourced claim (likely conflating **Frappe Cloud's** own AWS hosting footprint — Frappe the company is India-based and Frappe Cloud does host substantially out of Mumbai — with the **self-hosted, open-source S3 backup mechanism's** configuration, which has no built-in regional default at all).
- Additionally, **in v16, S3/offsite backup integration is being split out of Frappe core into a separate app** (`frappe/offsite_backups`), per an active Frappe Forum thread — not relevant to the v15 target today, but a forward-compatibility fact the Deferred section doesn't mention, and worth knowing before any v16 migration.

- Source (fetched directly, primary): [Upload Backups to Amazon S3 — docs.frappe.io/erpnext/aws_s3](https://docs.frappe.io/erpnext/aws_s3)
- Source: [Missing S3 Bucket Region causes boto3 error — GitHub issue #16498](https://github.com/frappe/frappe/issues/16498)
- Source: [S3 backup settings - no region 'af-south-1' — GitHub issue #23234](https://github.com/frappe/erpnext/issues/23234)
- Source: [State of S3 Backups in v16 — Frappe Forum](https://discuss.frappe.io/t/state-of-s3-backups-in-v16/155998)

**Recommend:** Rewrite AD-10 to drop the "Frappe's verified default region" framing entirely. The region choice (`ap-south-1` / Mumbai) is a **valid and sensible choice on its own merits** (matches the PRD's India data-residency decision, PRD §10.4), but it should be justified as *"our own choice, driven by data residency,"* not as *"Frappe's own default"* — because that second claim does not appear to be true. This is exactly the kind of asserted-not-verified claim promoted into a binding architectural rule that the review was asked to catch.

---

## 8. DNS-based multitenancy (site name == domain) — CONFIRMED ACCURATE

The Consistency Conventions table states site name must exactly equal the tenant's domain, calling it a "Frappe DNS-multitenancy requirement." Confirmed: `bench config dns_multitenant on`, then `bench new-site <domain>` where the site folder name is created to match the domain exactly, and the request handler dispatches by hostname.

- Source: [Setup Multitenancy — docs.frappe.io](https://docs.frappe.io/framework/user/en/bench/guides/setup-multitenancy)
- Source: [How to Set Up a New Site with DNS Multitenancy — finbyz.tech](https://finbyz.tech/erpnext/wiki/dns-based-multitenancy-(new-site))

**Verdict: accurate.**

---

## 9. `bench setup production` (Nginx + Gunicorn + Supervisor) — CONFIRMED ACCURATE

Confirmed current: `sudo bench setup production` automates Nginx + Gunicorn + Supervisor configuration; Supervisor keeps Frappe processes running and auto-restarts on crash; `bench setup nginx` / `bench setup supervisor` generate the respective configs. Matches the spine's "Web/process | Nginx + Gunicorn, managed by Supervisor (`bench setup production` defaults)" claim exactly.

- Source: [Setup Production — docs.frappe.io](https://docs.frappe.io/framework/user/en/bench/guides/setup-production)

**Verdict: accurate.**

---

## 10. Redis "latest stable compatible with Frappe v15" — appropriately hedged, not a stale-fact risk

The Stack table doesn't pin a specific Redis version, just "latest stable compatible with Frappe v15 (cache + queue)." This is a reasonable, low-risk hedge rather than an assertion of a specific fact that could go stale — no issue found. (Note for awareness, not a finding: Redis itself is now on the 8.x line, and Valkey — the Linux Foundation Redis fork — is a viable drop-in alternative on 9.1.x as of mid-2026; the document doesn't need to name either, since it deliberately avoided over-specifying here.)

---

## Summary Table

| Claim | Verified? | Status |
|---|---|---|
| Frappe v15 → Python 3.11+/Node 18+/MariaDB 10.3.x | Yes, matches official docs | OK |
| Frappe v16 exists, needs Python 3.14/Node 24 | Yes, matches official docs/forum | OK (nuance: v16 GA'd 7 months ago, more mature than implied) |
| ERPNext v15 = current recommended stable | Yes, per official GitHub wiki | OK (tension with Frappe's own v16 marketing not acknowledged) |
| MariaDB 10.6+ floor | **No — 10.6 hit EOL July 6, 2026, 4 days before doc date** | STALE |
| Node.js 18+ | Matches Frappe's stated floor, but Node 18 itself EOL since Apr 2025 | STALE FLOOR, unflagged |
| Ubuntu 22.04+ | Still in support until Apr 2027 | OK, minor |
| DNS multitenancy (site name == domain) | Yes | OK |
| `bench setup production` (Nginx/Gunicorn/Supervisor) | Yes | OK |
| AD-10: S3 backup defaults to ap-south-1 "Frappe's verified default" | **No primary source supports this; contradicted by docs/source/issues** | LIKELY INCORRECT |

## Recommended Actions

1. **AD-10 (highest priority):** Remove the "Frappe's own verified default region" framing. Re-justify `ap-south-1` purely on the India data-residency requirement (PRD §10.4), since that's a decision this project made, not a fact about Frappe.
2. **Stack table — MariaDB:** Bump the floor from "10.6+" to "10.11+" (current LTS) and note that 10.6 reached EOL July 6, 2026.
3. **Stack table — Node.js:** Clarify that "18+" is Frappe's documented floor but the actual deployment target should be Node 20 LTS or 22 LTS, since Node 18 has been EOL since April 2025.
4. **v15/v16 assumption footnote:** Soften the "documentation maturity" framing — v16 has been GA since December 2025 and is marketed by Frappe as production-ready; the real reason to stay on v15 (if there is one beyond "it's still officially the recommended stable branch") should be stated plainly rather than implying v16 is unproven.
5. Consider a one-line addition to Deferred noting that v16 moves S3/offsite backup out of core into a separate app (`frappe/offsite_backups`), which is relevant context if/when the v16 migration referenced in Deferred happens.
