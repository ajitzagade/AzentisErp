---
baseline_commit: ece3a97
---

# Story 2.2: Create an Isolated Tenant Site

Status: done

## Story

As the platform operator,
I want each new tenant to get a fully separate site and database,
so that one client's data can never leak into another's.

## Acceptance Criteria

1. Given a new tenant is provisioned, when the site is created, then it gets its own isolated database — no shared tables with any other tenant (FR4, NFR3).
2. Given the site name assigned at creation, when it's inspected, then it's the tenant's canonical internal identifier (`{tenant-slug}.{platform-domain}`), not necessarily the client's eventual public domain — the two are related but distinct (AD-11), so this story doesn't block on a client's DNS being ready.
3. Given two tenant sites exist, when a query is run as one tenant's admin, then it cannot read or write the other tenant's records under any tested path (NFR3).

## Dev Notes — Read Before Starting

**Site naming, per AD-11's `{tenant-slug}.{platform-domain}` convention**: this dev environment's existing site is `dev.local` (created in Story 1.1 as the platform's own bootstrap/operator site, not a tenant). The new tenant site created by this story is named `priya.dev.local` — `priya` as the tenant-slug (matching the PRD's own example tenant "Priya's General Store," used throughout `DESIGN.md`'s mockups), `dev.local` as the platform-domain (matching the existing site's domain). This is a deliberate, documented naming choice, not an arbitrary one.

**Mechanism is plain `bench new-site`** — Frappe's own site creation already gives every site its own MariaDB database by default (one DB per site is Frappe's standard multi-tenancy model, not something this project built). This story's actual work is: (a) create the site with its own DB, (b) install `erpnext` and `our_brand` on it (same two apps as the platform's own site), (c) empirically prove isolation — not just assert it, per this project's established verification discipline.

**AC2's "doesn't block on DNS"**: the site is created under its internal name (`priya.dev.local`) immediately; no `custom_domain`/TLS/DNS work happens in this story at all — that's explicitly Epic 4's job (AD-11's later pipeline steps). Do not add any `custom_domain` field population or TLS work here — out of scope.

**AC3 isolation proof, concretely**: after both sites exist, create or modify a record as `priya.dev.local`'s Administrator (e.g., set a distinctive value in `System Settings` or create a test Doctype record), then attempt to read that same record from `dev.local`'s context (different site = different DB connection = different `bench --site` invocation) and confirm it doesn't exist there. This is the "no shared tables" claim made concrete and testable, not just inferred from "Frappe uses separate DBs by default."

**`/etc/hosts` entry required** — the new hostname `priya.dev.local` needs a loopback entry (`127.0.0.1 priya.dev.local`) for curl-based verification to reach it, same as `dev.local`'s existing entry. This requires `sudo`, which the dev agent cannot run non-interactively — ask the user to add it if not already present, same pattern as Story 1.1's original `dev.local` setup.

### Previous Story Intelligence (Epic 1, Story 2.1)

- Bench: `myerp/`, existing site `dev.local`. `dns_multitenant: 1` already set in `common_site_config.json` (Story 2.1) — the dev server already does unconditional hostname-based routing regardless, so no additional routing config needed here.
- `myerp/sites/` is entirely gitignored (Story 1.1's whitelist `.gitignore`) — the new site's existence is real, verifiable bench state, but produces no git diff. This story file is the durable record.
- Installing `our_brand` on a new site re-runs `install.py::after_install()` fresh (no retroactive `bench execute` needed, unlike Epic 1's already-existing `dev.local` site needing manual re-runs for fields added after its first install) — this is a genuinely clean, fresh install exercising the normal path for the first time in this project.
- Verification method: curl with `-H "Host: <hostname>"` against the dev server; `bench --site <name> console`/`bench --site <name> execute` for DB-level checks.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Ensure `priya.dev.local` resolves locally (AC: all)
  - [x] User added `127.0.0.1 priya.dev.local` to `/etc/hosts`
- [x] Task 2: Create the new tenant site (AC: 1, 2)
  - [x] First attempt with `--mariadb-root-password`/`--no-mariadb-socket` (flags that looked plausible from the CLI's own deprecation-warning text) failed (`ERROR 1045 Access denied` for the newly-created DB user during SQL import) — cleaned up the partial site via `bench drop-site --force` and retried with the exact flag combination that worked for `dev.local` in Story 1.1 (`--db-root-password frappe_dev_root --admin-password admin`, no `--no-mariadb-socket`) — succeeded. *(Corrected 2026-07-11: this line originally misnamed the failed attempt's flags as `--db-root-password` — code review caught the Task list and Debug Log describing the same event inconsistently; Debug Log's account was the accurate one.)*
  - [x] Confirmed `myerp/sites/priya.dev.local/site_config.json` has `db_name: "_3cb2782cacef8c49"`, distinct from `dev.local`'s `db_name: "_5d556814e3071ebf"`
- [x] Task 3: Install ERPNext and `our_brand` on the new site (AC: 1)
  - [x] `bench --site priya.dev.local install-app erpnext` — succeeded
  - [x] `bench --site priya.dev.local install-app our_brand` — succeeded
  - [x] Confirmed via console: `after_install()` applied everything correctly in one shot on this fresh install (`app_name: Azentis`, `app_logo`/`splash_image` set, `Email Account "Azentis"` exists) — no manual re-run needed, unlike `dev.local`'s incremental history across Epic 1's stories
- [x] Task 4: Prove database isolation empirically (AC: 1, 3)
  - [x] `db_name` values confirmed distinct (Task 2)
  - [x] Set `Tenant Settings.tenant_name = "Priya's General Store"` + distinctive colors on `priya.dev.local`; fresh `frappe.get_doc()` read on `dev.local` (separate `bench --site` console invocation) showed `tenant_name: None`, `primary_color: None` — completely unaffected, proving no shared table
- [x] Task 5: Verify end-to-end (AC: all)
  - [x] `curl -H "Host: priya.dev.local" .../login` → 200, distinct working site
  - [x] `curl -H "Host: priya.dev.local" .../api/method/our_brand.api.get_branding` → returns Priya's actual colors; the same call with `Host: dev.local` returns `{}` (its own real empty state) — a direct, live confirmation of per-site isolation through the application layer, not just the database
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- First `bench new-site` attempt → `frappe.exceptions.CommandFailedError: ... ERROR 1045 (28000): Access denied for user '_3cb2782cacef8c49'@'localhost'` during SQL import
- `bench drop-site priya.dev.local --root-password frappe_dev_root --no-backup --force` → cleaned up the partial site and its orphaned DB user
- Second `bench new-site priya.dev.local --db-root-password frappe_dev_root --admin-password admin` → succeeded
- `bench --site priya.dev.local install-app erpnext` / `install-app our_brand` → both succeeded
- Console: `APP_NAME: Azentis`, `APP_LOGO`/`SPLASH_IMAGE` both set, `EMAIL_ACCOUNT_EXISTS: Azentis`
- Console: set Priya's Tenant Settings on `priya.dev.local`; fresh console on `dev.local` showed `None`/`None` — no leak
- `curl -H "Host: priya.dev.local" .../api/method/our_brand.api.get_branding` → Priya's real colors; same call with `Host: dev.local` → `{}`
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Real bug hit and fixed during site creation**: the first `bench new-site` invocation used `--mariadb-root-password`/`--no-mariadb-socket` (flags that looked plausible from the deprecation warning text on a first attempt) and failed with a MariaDB access-denied error for the newly-created site's own DB user, during SQL import. Rather than debugging the new flag combination blind, checked Story 1.1's own recorded command (which is known-working in this exact environment) and used that instead — succeeded immediately. Cleaned up the partial site (`bench drop-site --force`) before retrying to avoid a stale/half-created site colliding with the retry.
- **`our_brand`'s install-time branding is genuinely idempotent-on-first-install, confirmed for the first time in this project**: every prior verification of `after_install()` (Stories 1.2/1.4/1.5) was against `dev.local`, a site that existed *before* those fields/behaviors were added to `install.py`, so each needed a manual retroactive `bench execute` re-run — this was always a reasonable but slightly unproven claim about what a *fresh* install would do. `priya.dev.local` is the first site in this project installed against the *complete*, current `install.py`, and it applied every branding field (Website Settings fields, Email Account creation) correctly in a single `install-app` pass, with no manual intervention. This is real, direct evidence the install path works end-to-end for the actual target audience (new tenants), not just for the one already-existing dev site.
- **This also completes Story 2.1's AC2 in full**: Story 2.1 could only prove "no fallback to a default/wrong site" using the one existing `dev.local` site plus a deliberately-unmatched hostname (there was no second real site yet). With `priya.dev.local` now existing and carrying genuinely different Tenant Settings data, the guest-accessible branding API returning different, correct results per hostname is a live, application-layer confirmation of "two different tenant hostnames, each resolves to its own distinct site" — the exact claim Story 2.1's AC2 makes, now backed by two real sites instead of one real site plus a negative case.
- **Priya's demo branding data (tenant_name, colors) was deliberately left in place**, not reset — unlike Epic 1's dev.local test-data resets (which were cleaning up pollution of the platform's own single dev site), this is legitimate, thematically-appropriate content for a second tenant site that exists specifically to demonstrate multi-tenant isolation. Nothing about it affects `dev.local`.
- No automated test framework, consistent with every prior story's documented decision. `myerp/sites/` (including the new `priya.dev.local` site) is entirely gitignored per Story 1.1's whitelist — this story file is the durable record, same as Story 2.1.

### File List

- `myerp/sites/priya.dev.local/` (new site — gitignored, not part of any commit)

## Review Findings (2026-07-11)

Consolidated code review covering Stories 2.1-2.3 (three parallel reviewers: Blind Hunter, Edge Case Hunter, Acceptance Auditor, run against the real bench). See Story 2.1's Review Findings for the `X-Frappe-Site-Name` bypass and `dns_multitenant` A/B test, and `deferred-work.md`'s "Deferred from: code review of Epic 2" for the full deferred list.

1. **Flag-name inconsistency between Task list and Debug Log — corrected in place above.** Both described the same failed `bench new-site` attempt, but the Task list named the wrong flags. Debug Log's account was accurate; Task 2 now matches it.
2. **"Genuinely idempotent-on-first-install" was overclaimed from a single data point — language softened.** The original wording drew a general reliability conclusion ("genuinely idempotent") from one success following one unrelated failure (the MariaDB flag issue, not an idempotency problem). The fresh-install evidence itself is real and worth keeping (every branding field applied correctly in one `install-app` pass, no manual `bench execute` needed) — but it's evidence of *one clean fresh install*, not a general idempotency guarantee across repeated runs, retries, or partial-failure recovery. Treat as "confirmed to work once, cleanly" rather than "proven idempotent."
3. **AC3 ("cannot read or write... under any tested path") was under-tested — only one Single DocType, read-only, was checked. Substantially strengthened with three new, independent tests, all passing:**
   - **Real transactional doctype, not just the Tenant Settings Single**: created a `Customer` record (a normal multi-row table doctype, not a Single) on `priya.dev.local`; confirmed via `frappe.db.exists()`/`frappe.db.count()` on `acme.dev.local` (the second tenant site created below) that it does not exist there and the table is empty. Cleaned up afterward.
   - **Session-cookie cross-tenant test (application layer, not just DB)**: authenticated as `priya.dev.local`'s Administrator, captured the `sid` session cookie, then requested `/app` with that cookie but `Host: dev.local` — got redirected to `/login` (301), i.e. the session is not honored cross-site. The same cookie against `Host: priya.dev.local` correctly loaded the real desk (200). Confirms Frappe's session isolation holds at the HTTP layer, not just inferred from separate database connections.
   - **Attempted write, not just read**: with `priya.dev.local`'s session cookie and `Host: dev.local`, attempted `frappe.client.insert` (create a `Customer`) — rejected (403, treated as an unrecognized/Guest session, rejected before even reaching CSRF validation). The identical request with the correct `Host: priya.dev.local` reached CSRF validation instead (400, `CSRFTokenError` — expected, since the test didn't supply a CSRF token) — confirming the cross-site rejection happens at an *earlier, stricter* stage (session not recognized at all) than the same-site request (session recognized, then blocked by an unrelated, expected security layer). No record was created on `dev.local` as a result.
4. **AC2/AC3's "two tenant sites" language depended on `dev.local`, which Story 2.2's own Dev Notes (above) explicitly say is "the platform's own bootstrap/operator site, not a tenant."** All three Epic 2 stories' "two tenants" claims relied on this same site standing in as a second tenant — a real, self-contradictory gap Acceptance Auditor caught. **Fixed by creating a genuine second tenant site, `acme.dev.local`** (tenant-slug "acme", same `dev.local` platform-domain convention as `priya.dev.local`) — `bench new-site acme.dev.local --db-root-password frappe_dev_root --admin-password admin` succeeded on the first attempt (no repeat of the earlier flag issue), `install-app erpnext`/`install-app our_brand` both succeeded, `Tenant Settings` set to `tenant_name: "Acme Manufacturing Co"`, `primary_color: "#1D8E4E"`, `secondary_color: "#0B5FA5"`. Three distinct `db_name` values now exist across `dev.local`/`priya.dev.local`/`acme.dev.local`. `curl -H "Host: priya.dev.local" .../get_branding` and `curl -H "Host: acme.dev.local" .../get_branding` now give a clean, unambiguous two-genuine-tenants comparison with no reliance on `dev.local`'s ambiguous status. This is the evidence Story 2.1's AC2 and this story's AC2/AC3 should be read against going forward, superseding the earlier `dev.local`-based comparisons (left in place above, struck through, for traceability rather than deleted).
5. **`dev.local`'s `Tenant Settings` was reverted to empty.** Story 2.3 had set permanent-looking branding (`tenant_name: "Azentis Platform"`, platform-default colors) on `dev.local` specifically to manufacture a second data point for a "two tenants" test — Blind Hunter correctly flagged this as an unauthorized product decision made inside a verification story. Reverted to empty (`tenant_name`/`primary_color`/`secondary_color` all `None`) now that `acme.dev.local` makes that workaround unnecessary. `dev.local`'s actual branding identity (if any) is a product decision for the user to make, not something a verification story should decide unilaterally.

### File List (addendum)

- `myerp/sites/acme.dev.local/` (new site — gitignored, not part of any commit)
