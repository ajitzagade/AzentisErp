---
epic: 4
title: One-Action Client Onboarding
status: approved
source: ../../epics.md
---

# Epic 4: One-Action Client Onboarding

Onboard a brand-new paying client — site, branding, modules, admin user, TLS, welcome email — in a single action, under 10 minutes, instead of repeating Epics 1–3's steps by hand every time.

**FRs covered:** FR6, FR11, FR12
**Architecture:** AD-7 (idempotent resumable pipeline), AD-8 (SSH-run CLI, no hosted API), AD-11 (TLS + domain-alias as separate resumable steps)

## Story 4.1: Stand Up Production Server Infrastructure

As the platform operator,
I want a real production server running the bench in production mode,
So that a real client can actually be onboarded onto working infrastructure, not just a local dev bench.

**Acceptance Criteria:**

**Given** an Ubuntu 22.04+ server (min 4GB RAM / 2 vCPU, India-hosted region per PRD §10.4)
**When** `bench setup production {user}` runs
**Then** Nginx, Gunicorn, and Supervisor are configured and the bench serves requests over HTTP

**Given** this story completes
**When** Epic 5's later stories (backups, firewall) run
**Then** they build on this same server — this story is not repeated per-tenant, it happens once

## Story 4.2: One-Action Provisioning Pipeline — Site, Branding, Modules, Admin

As the platform operator,
I want one command that creates a fully configured tenant site,
So that I never repeat Epics 1–3's setup steps by hand per client.

**Acceptance Criteria:**

**Given** client name, domain, admin email, module preset, logo, and colors
**When** the pipeline runs
**Then** it creates the site (canonical internal name, AD-11), installs ERPNext + `our_brand`, creates a populated Tenant Settings record, applies the selected preset (Story 3.4), and sets the admin user — as one operator-triggered action (FR6, FR11)

**Given** a partial failure mid-pipeline (e.g., site created but app install fails)
**When** the pipeline is re-run
**Then** it resumes safely from the failed step rather than erroring or duplicating work (AD-7)

**Given** this story's steps complete (excluding TLS/email, Stories 4.3–4.4)
**When** elapsed time is measured
**Then** it's well under the 10-minute SM-2 target on its own

## Story 4.3: TLS Issuance and Custom Domain Binding

As the platform operator,
I want TLS and the client's real domain wired up as part of onboarding,
So that a client never lands on an insecure or wrong-domain site.

**Acceptance Criteria:**

**Given** a newly provisioned site (Story 4.2)
**When** its `custom_domain`'s DNS already resolves
**Then** TLS is requested and the domain is bound automatically (FR12, AD-11)

**Given** DNS isn't resolving yet
**When** the pipeline runs
**Then** this step is skipped without blocking the rest of onboarding, and is safely re-runnable later once DNS is ready (UJ-1's explicit edge case)

## Story 4.4: Send Branded Welcome Email

As a new tenant's admin,
I want a branded welcome email with my login link,
So that I can access my instance without asking Ajit for help.

**Acceptance Criteria:**

**Given** onboarding completes (Stories 4.2–4.3)
**When** the welcome email step runs
**Then** it sends using Epic 1's branded template (Story 1.4) with a working login link

**Given** outbound email transport isn't configured on the server (a one-time ops precondition, previously left unstated in the architecture spine's Deferred list)
**When** this step runs without it
**Then** it fails loudly and is clearly reported — never silently completing onboarding while the client never receives their link
