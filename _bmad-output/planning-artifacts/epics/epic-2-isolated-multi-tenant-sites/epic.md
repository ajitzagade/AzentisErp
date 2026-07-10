---
epic: 2
title: Isolated Multi-Tenant Sites
status: approved
source: ../../epics.md
---

# Epic 2: Isolated Multi-Tenant Sites

Run multiple client sites on one server, each with its own isolated database, each reachable at its own domain/subdomain, each carrying its own branding from Epic 1.

**FRs covered:** FR4, FR5
**NFRs relevant:** NFR1 (Scalability — DB-per-tenant is the scaling mechanism), NFR3 (Data Isolation & Security)
**Architecture:** deployment topology (T1, T2…TN each own DB on one bench), Consistency Conventions (site name = canonical internal identifier, distinct from `custom_domain` — AD-11), "no cross-site DB connections, ever" rule

## Story 2.1: Enable DNS-Based Multi-Tenant Routing

As the platform operator,
I want the bench to route incoming requests to the correct site by domain,
So that each tenant can be reached at its own address.

**Acceptance Criteria:**

**Given** `dns_multitenant` is enabled on the bench
**When** a request arrives for a given hostname
**Then** it's routed to the matching site's database and assets (FR5)

**Given** two different tenant hostnames
**When** each is requested
**Then** each resolves to its own distinct site — no fallback to a default/wrong site

## Story 2.2: Create an Isolated Tenant Site

As the platform operator,
I want each new tenant to get a fully separate site and database,
So that one client's data can never leak into another's.

**Acceptance Criteria:**

**Given** a new tenant is provisioned
**When** the site is created
**Then** it gets its own isolated database — no shared tables with any other tenant (FR4, NFR3)

**Given** the site name assigned at creation
**When** it's inspected
**Then** it's the tenant's canonical internal identifier (`{tenant-slug}.{platform-domain}`), not necessarily the client's eventual public domain — the two are related but distinct (AD-11), so this story doesn't block on a client's DNS being ready

**Given** two tenant sites exist
**When** a query is run as one tenant's admin
**Then** it cannot read or write the other tenant's records under any tested path (NFR3)

## Story 2.3: Tenant Site Carries Its Own Branding

As the platform operator,
I want a newly created tenant site to work with Epic 1's branding system independently,
So that adding a tenant doesn't require any branding rework.

**Acceptance Criteria:**

**Given** a new tenant site has ERPNext and `our_brand` installed on it
**When** it's accessed
**Then** it has its own independent Tenant Settings record (Story 1.5), separate from every other tenant's

**Given** two tenants each set different `primary_color` values
**When** each is viewed
**Then** each shows only its own color — no cross-tenant branding bleed
**And** no platform-wide view queries across tenant databases to produce this — each site is inspected independently (spine's "no cross-site DB connections" rule)
