---
epic: 5
title: Platform Reliability & Upstream Maintainability
status: approved
source: ../../epics.md
---

# Epic 5: Platform Reliability & Upstream Maintainability

Trust that the platform stays online (backups, restricted access) and stays safely patchable against upstream Frappe/ERPNext security releases without breaking any tenant's customizations.

**FRs covered:** FR13, FR14, FR15, FR16
**Architecture:** AD-9 (staging = one more site on the production bench), AD-10 (S3-compatible backups, India region)

## Story 5.1: Automated Offsite Backups

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

## Story 5.2: Restrict Network Access

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

## Story 5.3: Create and Maintain a Staging Site

As the platform operator,
I want a staging site on the same production bench,
So that I have somewhere safe to test upstream changes before they touch a paying client.

**Acceptance Criteria:**

**Given** the production bench (Story 4.1)
**When** a staging site is created
**Then** it exists as one more site on that same bench — not a separate server (AD-9) — and mirrors the customization stack (`our_brand` + the pinned ERPNext dependency) any tenant site would have

## Story 5.4: Staged Upstream Update Rollout

As the platform operator,
I want to verify an upstream Frappe/ERPNext update on staging before it touches any tenant,
So a bad update never hits a paying client first.

*(Revised 2026-07-10 — updates now mean re-pinning the pinned ERPNext/Frappe dependency to a newer upstream commit, not merging a fork; there is no fork to merge.)*

**Acceptance Criteria:**

**Given** a new upstream ERPNext/Frappe release
**When** `apps/erpnext` (or `apps/frappe`) is re-pinned to the new commit/tag (`git fetch origin && git checkout <new-commit>` against the pinned, unforked upstream repo, followed by `bench migrate`)
**Then** it's applied and tested on the staging site (Story 5.3) first

**Given** staging verification passes
**When** the update is rolled out
**Then** the same commit/tag pin is applied to production tenant sites only after that verification — never before (FR16)

## Story 5.5: Prove Customization Isolation via a Real Upstream Update

As the platform operator,
I want direct evidence that our customizations survive an upstream update,
So "isolation" isn't just a design intention.

*(Revised 2026-07-10 — "via a Real Merge" renamed; without a fork, there's no merge to perform. The proof now comes from re-pinning to a new upstream commit and confirming nothing in `our_brand` breaks.)*

**Acceptance Criteria:**

**Given** a real upstream re-pin is performed (Story 5.4's process, on staging)
**When** the new commit is checked out and `bench migrate` completes
**Then** `our_brand` requires zero code changes to keep working (FR15's stated testable consequence) — and if anything in `our_brand` *does* need adjustment because an upstream hook/API changed, that's documented as a precedent for future updates
