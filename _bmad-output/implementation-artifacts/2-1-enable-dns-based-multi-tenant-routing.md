---
baseline_commit: ece3a97
---

# Story 2.1: Enable DNS-Based Multi-Tenant Routing

Status: done

## Story

As the platform operator,
I want the bench to route incoming requests to the correct site by domain,
so that each tenant can be reached at its own address.

## Acceptance Criteria

1. Given `dns_multitenant` is enabled on the bench, when a request arrives for a given hostname, then it's routed to the matching site's database and assets (FR5).
2. Given two different tenant hostnames, when each is requested, then each resolves to its own distinct site — no fallback to a default/wrong site.

## Dev Notes — Read Before Starting

**`dns_multitenant` is a production-Nginx-config-generation flag, not something that changes dev-server routing behavior.** Investigated the actual mechanism before writing this story:

- The `bench` CLI (a separate installed package, `frappe_bench`, not part of the `frappe`/`erpnext` apps under `myerp/apps/`) reads `common_site_config.json`'s `dns_multitenant` key in exactly one place: `bench/config/nginx.py`, when generating a production Nginx config via `bench setup nginx`. When true, Nginx routes every site by `server_name`/hostname on shared ports (real multi-tenant SaaS behavior); when false/unset, each site needs its own assigned port and Nginx generates one server block per port. **This only matters for a production Nginx deployment** (Epic 4/5's concern) — it has zero effect on `bench start`'s dev server.
- The dev server's actual site routing is unconditional and already hostname-based, with no flag gating it: `frappe/app.py::init_request()` resolves the site via `get_site_name(request.host)` (`frappe/utils/__init__.py:593-594`, literally `hostname.split(":", 1)[0]`), which becomes the folder name Frappe looks up under `sites/`. If `sites/<hostname>/site_config.json` doesn't exist, `frappe.init()` leaves `frappe.local.conf.db_name` unset and `init_request()` raises `NotFound` (404) — **there is no fallback path to a default site in this code**, confirming AC2's "no fallback to a default/wrong site" is already Frappe's stock behavior for the dev server, not something this story needs to build.
- **What this story actually delivers**: (a) set `dns_multitenant: 1` in `common_site_config.json` — this is the platform's own documented intent for when a production Nginx config eventually gets generated (Epic 4/5), and satisfies AC1's literal wording ("dns_multitenant is enabled on the bench"), even though it has no observable effect on `bench start`'s routing today; (b) empirically prove the underlying hostname-based routing mechanism AC1/AC2 actually describe, using curl against the dev server directly (bypassing Nginx entirely, since there is no Nginx in this dev environment) with different `Host` headers.

**Scope boundary vs. Story 2.2**: proving AC2's "two different tenant hostnames, each resolves to its own distinct site" fully requires two actual sites to exist. Creating a second, fully-provisioned tenant site (ERPNext + `our_brand` installed) is explicitly Story 2.2's job ("Create an Isolated Tenant Site"), not this story's. This story proves the *mechanism* using what's available now: the existing `dev.local` site correctly resolves, and a request for a hostname with **no** matching site folder correctly 404s rather than silently falling back to `dev.local` (or any other site) — that's the actual behavior AC2's "no fallback" clause is testing, and it's fully provable without a second real site. Story 2.2's own creation of a second site (naming decided there: `{tenant-slug}.{platform-domain}` per AD-11) will be a second, independent confirmation of the same mechanism this story enables, not a re-test this story needs to duplicate.

### Previous Story Intelligence (Epic 1)

- Bench: `myerp/`, existing site `dev.local`. `common_site_config.json` currently has no `dns_multitenant` key.
- Verification method: plain curl with `-H "Host: <hostname>"` against `http://127.0.0.1:8000` (the dev server) — already the established pattern from every Epic 1 story for testing hostname-scoped behavior.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Enable `dns_multitenant` in bench config (AC: 1)
  - [x] Set `dns_multitenant: 1` in `myerp/sites/common_site_config.json`
- [x] Task 2: Prove hostname-based routing to the existing site (AC: 1)
  - [x] `curl -H "Host: dev.local" .../api/method/frappe.ping` → `200 {"message":"pong"}`, confirming correct resolution to `dev.local`'s DB
- [x] Task 3: Prove no fallback to a default/wrong site for an unmatched hostname (AC: 2)
  - [x] `curl -H "Host: nonexistent-tenant.dev.local" .../api/method/frappe.ping` → `404`, body explicitly reads "nonexistent-tenant.dev.local does not exist" — proves per-hostname folder lookup (Frappe names the exact hostname it failed to find), not a silent fallback to `dev.local`'s content
- [x] Task 4: Document and hand off to Story 2.2 (AC: all)
  - [x] Recorded below: full two-real-site confirmation of AC2 completes naturally once Story 2.2 creates its tenant site
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `curl -H "Host: dev.local" .../api/method/frappe.ping` → `200 {"message":"pong"}`
- `curl -H "Host: nonexistent-tenant.dev.local" .../api/method/frappe.ping` → `404`, `"nonexistent-tenant.dev.local does not exist"`
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **This story's actual change is a one-line config flag in a gitignored file** (`myerp/sites/common_site_config.json` — the whole `sites/` directory is intentionally excluded from version control per Story 1.1's whitelist `.gitignore`, since it's instance-specific runtime state, not application code). This story file is the durable record of that change; there is nothing to see in a code diff for this story, matching Story 1.1's own precedent for bench-level config work.
- **Root-caused what `dns_multitenant` actually does before touching anything**: read the `bench` CLI package's own source (`bench/config/nginx.py`) rather than assuming from the AC's name — confirmed it is exclusively a production Nginx config-generation flag with zero effect on `bench start`'s dev server, which already does unconditional hostname-based site routing (`frappe/app.py::init_request()` → `get_site_name(request.host)`). This meant AC2's "no fallback to a default/wrong site" was already true stock Frappe behavior, not something to build — the story's real work was setting the flag for future production use (Epic 4/5) and *proving* the existing mechanism behaves as the AC describes.
- **AC2 full confirmation is intentionally partial here, by design, not an oversight**: proving "two different tenant hostnames each resolve to their own distinct site" fully needs two real sites; this story proves the "no fallback" half using the one existing site plus an intentionally-unmatched hostname. Story 2.2 creating a second real site was the natural second half of this same proof — no separate re-verification pass was needed, since it's the same underlying mechanism.
- **Addendum, superseded — see Review Findings below.** This note originally claimed AC2 was fully confirmed via `dev.local` vs. `priya.dev.local`. Code review (2026-07-11) correctly flagged that `dev.local` is documented elsewhere as "the platform's own operator site, not a tenant," so that comparison was not the clean "two tenants" proof it was presented as. Superseded by a genuine two-tenant comparison (`priya.dev.local` vs. `acme.dev.local`) — see Review Findings.
- No automated test framework, consistent with every Epic 1 story's documented decision.

### File List

- `myerp/sites/common_site_config.json` (modified — `dns_multitenant: 1`; gitignored, not part of any commit)

## Review Findings (2026-07-11)

Consolidated code review covering Stories 2.1-2.3 (three parallel reviewers: Blind Hunter, Edge Case Hunter, Acceptance Auditor, run against the real bench rather than a diff, since Epic 2's changes are entirely in gitignored `myerp/sites/` runtime state). See `deferred-work.md`'s "Deferred from: code review of Epic 2" entry for the full list of deferred findings and Stories 2.2/2.3 for the rest of this batch's fixes.

**Findings specific to this story:**

1. **[CRITICAL, documented not patched — Frappe core, out of reach per AD-1] `X-Frappe-Site-Name` header bypasses `Host`-header routing entirely.** Blind Hunter found, and I independently reproduced: `frappe/app.py::init_request()` resolves the site as `_site or request.headers.get("X-Frappe-Site-Name") or get_site_name(request.host)` — the `X-Frappe-Site-Name` header takes priority over `Host`. `curl -H "Host: dev.local" -H "X-Frappe-Site-Name: priya.dev.local" .../get_branding` returns Priya's colors, not `dev.local`'s; the reverse also works. This is a real routing bypass that undermines this story's own "no fallback to a default/wrong site" claim (AC2) whenever this header reaches the app unfiltered. It's Frappe core behavior (`frappe/app.py`), not `our_brand` code — AD-1 forbids modifying it. **The only correct fix is at the production Nginx layer** (Epic 4/5): the reverse proxy must set/overwrite `X-Frappe-Site-Name` itself (or strip any client-supplied value) before proxying to gunicorn, a standard Frappe production-hardening step. Logged as a **must-do** item in `deferred-work.md`, not an optional one — this dev environment has no Nginx in front of it, so the bypass is currently reachable directly, but any production deployment without this mitigation would have a real cross-tenant isolation hole.
2. **AC1's "assets" clause was inaccurate as originally verified — corrected.** Original verification only exercised the API (`frappe.ping`). Acceptance Auditor found, and I confirmed via curl, that `/assets/...` (the compiled JS/CSS/image bundle) is **not** hostname-scoped at all — `curl -H "Host: totally-fake-garbage.local" .../assets/frappe/images/frappe-favicon.svg` returns `200`, same as any real hostname. This is expected/correct (compiled assets are identical build output shared by every site on one bench, not per-tenant data — `our_brand.css`, `branding.js`, etc. are meant to be the same file everywhere), but AC1's literal wording ("routed to the matching site's... assets") is misleading if read as "assets are hostname-isolated." The site-scoped equivalent — user-uploaded files (`/private/files/...`) — **is** correctly hostname-isolated (confirmed via `init_request()` routing through the same site-resolution path, and via Edge Case Hunter's independent probe returning 403 both cross-site and unauthenticated). Read AC1's "assets" as "the site's own uploaded files," not "the compiled static bundle."
3. **AC1's causal framing ("given `dns_multitenant` is enabled... then routed") was proven only by static code reading, not an empirical test — now empirically confirmed.** Temporarily set `dns_multitenant: 0`, re-ran the exact same `dev.local`/unmatched-hostname curl checks from Task 2/3 — identical results (`200`/`404`) with the flag off as with it on. Restored to `1` afterward. This closes the gap Blind Hunter flagged: the "zero effect on dev routing" conclusion is now backed by a direct A/B test, not just reading `bench/config/nginx.py`'s source.
4. **AC2 full confirmation, corrected**: the original addendum (struck through above) used `dev.local` as a stand-in second "tenant," which Story 2.2's own Dev Notes explicitly say it is not. Story 2.2 subsequently created a genuine second tenant site (`acme.dev.local`, alongside `priya.dev.local`) specifically to give this AC an unambiguous two-tenant proof — see Story 2.2's Review Findings for the exact evidence (`priya.dev.local` and `acme.dev.local` each returning only their own branding via `get_branding()`, with `dev.local` not involved in the comparison at all).
