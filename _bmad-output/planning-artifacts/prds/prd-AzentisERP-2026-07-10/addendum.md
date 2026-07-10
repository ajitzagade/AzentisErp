# Addendum: AzentisERP — Technical Mechanics

*Companion to `prd.md`. This captures implementation-level detail (commands, field lists, file layout) that supports the PRD's capabilities but isn't itself a requirement. Source: `docs/product.md`, preserved here for architecture/epics handoff.*

## Tech Stack

- Backend: Python 3.10+, Frappe Framework
- Frontend: JavaScript (Frappe's desk UI), Jinja templates
- Database: MariaDB 10.6+
- Cache/Queue: Redis
- Web Server: Nginx + Gunicorn (via Supervisor)
- CLI Tool: Frappe Bench
- OS: Ubuntu 22.04+ (production)

## Local Dev Setup (supports MVP §6.1 "local dev environment")

1. Install prerequisites: Python 3.10+, Node 18+, MariaDB 10.6+, Redis, wkhtmltopdf, yarn, git, pip.
2. `pip install frappe-bench`
3. `bench init myerp --frappe-branch version-15` *(stock Frappe Framework from official `frappe/frappe` — not forked; PRD §10.7 decision)*
4. `bench get-app erpnext https://github.com/OUR_ORG/erpnext --branch version-15` *(forked ERPNext under our org)*
5. `bench new-site dev.local`
6. `bench --site dev.local install-app erpnext`
7. `bench start`
8. Verify via setup wizard, confirm all modules load.

## Branding App (supports FR-1–FR-3)

- `bench new-app our_brand` (rename to final product/brand name — PRD §1 flags this as unconfirmed working title).
- `hooks.py`: `app_name`, `app_title`, `app_publisher`, `app_description`, `app_logo_url`, `website_context` overrides.
- Assets under `our_brand/public/images/` (logo, favicon).
- `our_brand/public/css/custom.css`: primary/accent colors, login styling, navbar, footer, splash — included via `app_include_css = ["/assets/our_brand/css/custom.css"]`.
- Login template override: `our_brand/templates/includes/login/`.
- Email template override: `our_brand/templates/emails/`.
- Install: `bench --site dev.local install-app our_brand`.
- **Constraint:** GPLv3 license notices and copyright headers stay untouched — only visible branding is replaced.

## Multi-Tenancy (supports FR-4–FR-6)

- `bench config dns_multitenant on`
- Second site test: `bench new-site client1.localhost`, install `erpnext` then `our_brand`.
- `provision_client.sh` automates: `bench new-site {domain}` → `install-app erpnext` → `install-app our_brand` → set admin password → run setup wizard via API/bench → `bench --site {domain} set-config` for branding.

## Tenant Settings DocType (supports FR-7–FR-8)

Single, per-site DocType with fields:
- `tenant_name`, `logo` (attach), `primary_color` (color), `secondary_color` (color), `favicon` (attach), `login_background` (attach), `email_sender_name`, `email_footer_text`, `enabled_modules` (table/multi-select), `custom_domain`.

Hooks: read Tenant Settings on page load → inject branding CSS dynamically; show/hide sidebar modules based on `enabled_modules`.

## Module Catalog (supports FR-9–FR-10)

- CRM: Leads, Opportunities, Customers, Sales Pipeline
- Sales: Quotations, Sales Orders, Sales Invoices
- Purchasing: Purchase Orders, Purchase Invoices, Suppliers
- Finance/Accounting: Chart of Accounts, General Ledger, GST, Payment Entries, Financial Statements
- HR: Employees, Attendance, Leave, Payroll
- Inventory/Stock: Items, Warehouses, Stock Entries, Stock Ledger
- Projects: Projects, Tasks, Timesheets, Gantt
- Manufacturing: BOM, Work Orders, Production Planning
- Assets: Asset Management, Depreciation
- Support/Helpdesk: Issues, SLA, Knowledge Base
- Website: CMS, Web Forms, Blog
- Workflows: Custom Workflows per DocType
- Reports/Dashboards: Report Builder, Query Reports, Dashboard Charts

**Presets:**
- Retail: Stock + POS + Accounts + CRM
- Services: Projects + CRM + HR + Accounts
- Manufacturing: Manufacturing + Stock + Purchasing + Accounts
- General: All modules enabled

**Dependency documentation needed:** e.g., Sales needs Accounting (per-module dependency map to be authored; ties to PRD Open Question 6).

## Production Deployment (supports FR-12–FR-14)

1. Ubuntu 22.04, min 4GB RAM / 2 vCPU to start.
2. `bench setup production {user}` — Nginx, Supervisor, Gunicorn.
3. `bench setup lets-encrypt {site_name}` per site.
4. DNS: each client domain → server IP.
5. Backups: `bench --site {site} backup` via cron (daily minimum), stored offsite (S3 or equivalent).
6. Monitoring: uptime checks, disk/memory alerts. *(Deferred beyond MVP — PRD §6.2.)*
7. Log rotation.
8. Firewall: allow only 80/443, restrict SSH.

## Client Onboarding Automation (supports FR-11)

Admin inputs: client name, domain, admin email, selected modules, logo, colors.
Script: provisions site → installs apps → applies branding → enables modules → creates admin user → sends welcome email.
Target: under 10 minutes per client (PRD SM-2).

## Update & Maintenance (supports FR-15–FR-16)

1. Track upstream Frappe/ERPNext releases.
2. `git fetch upstream && git merge upstream/version-15`.
3. Resolve conflicts (expected minimal — branding app is separate).
4. Test on staging before production.
5. `bench update` on production (`--no-backup` only if backup already taken).
6. Roll out to all tenant sites at once. *(Formal automation of this rollout deferred beyond MVP — PRD §6.2; first 1-2 cycles done manually.)*

## Architecture Summary (as originally sketched)

```
┌─────────────────────────────────────────┐
│            Our Production Server         │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ Site A   │  │ Site B   │  │ Site C   │  │
│  │ Dairy Co │  │ RetailX  │  │ BuildCo  │  │
│  │ DB: A    │  │ DB: B    │  │ DB: C    │  │
│  │ Modules: │  │ Modules: │  │ Modules: │  │
│  │ Stock,   │  │ POS,     │  │ Projects │  │
│  │ Accounts │  │ Stock,   │  │ Accounts │  │
│  │          │  │ CRM      │  │ HR       │  │
│  └─────────┘  └─────────┘  └─────────┘  │
│                                          │
│  Shared Codebase:                        │
│  - Frappe Framework                      │
│  - ERPNext (our fork)                    │
│  - our_brand (custom branding app)       │
│                                          │
│  Nginx → Gunicorn → Frappe/ERPNext       │
│  MariaDB (separate DB per site)          │
│  Redis (cache + queue)                   │
└─────────────────────────────────────────┘
```

*Full architectural decisions (fork strategy, hook boundaries, DB-per-tenant confirmation) belong to `bmad-architecture`, not this addendum — this is the mechanics as scoped going in.*
