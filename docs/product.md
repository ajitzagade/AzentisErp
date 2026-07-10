# Project: Build a Production-Ready, Multi-Tenant ERP/CRM SaaS Platform

## Foundation

Fork and customize **Frappe Framework** (`github.com/frappe/frappe`) and **ERPNext** (`github.com/frappe/erpnext`) to build a fully rebranded, self-hosted, multi-tenant ERP/CRM SaaS platform.

This is NOT a build-from-scratch project. We are forking an existing open-source ERP (ERPNext, licensed GPLv3) and making it our own product.

---

## Tech Stack (inherited from Frappe/ERPNext)

- **Backend:** Python 3.10+, Frappe Framework
- **Frontend:** JavaScript (Frappe's desk UI), Jinja templates
- **Database:** MariaDB 10.6+
- **Cache/Queue:** Redis
- **Web Server:** Nginx + Gunicorn (via Supervisor)
- **CLI Tool:** Frappe Bench
- **OS:** Ubuntu 22.04+

---

## Step-by-Step Build Plan

### Phase 1: Local Development Setup

1. Install prerequisites: Python 3.10+, Node 18+, MariaDB 10.6+, Redis, wkhtmltopdf, yarn, git, pip.
2. Install Frappe Bench CLI: `pip install frappe-bench`
3. Initialize bench: `bench init myerp --frappe-branch version-15`
4. Clone our ERPNext fork: `bench get-app erpnext https://github.com/OUR_ORG/erpnext --branch version-15`
5. Create first dev site: `bench new-site dev.local`
6. Install ERPNext on site: `bench --site dev.local install-app erpnext`
7. Start dev server: `bench start`
8. Verify: open browser, complete setup wizard, confirm all modules load.

### Phase 2: Create Our Custom Branding App

Do NOT edit ERPNext or Frappe source directly for branding. Create a separate custom app so upstream updates remain mergeable.

1. `bench new-app our_brand` (replace "our_brand" with our actual app name)
2. In `our_brand/hooks.py`, set:
   - `app_name = "our_brand"`
   - `app_title = "OurBrand ERP"` (our product name)
   - `app_publisher = "Our Company Name"`
   - `app_description = "Unified Business Management Platform"`
   - `app_logo_url = "/assets/our_brand/images/logo.png"`
   - `website_context` overrides for brand name, footer, splash
3. Add our logo, favicon, and brand assets under `our_brand/public/images/`.
4. Add custom CSS in `our_brand/public/css/custom.css` to override:
   - Primary colors, accent colors
   - Login page styling
   - Navbar brand logo and text
   - Footer text (remove "Built on Frappe/ERPNext")
   - Splash/loading screen
5. In `hooks.py`, include the CSS: `app_include_css = ["/assets/our_brand/css/custom.css"]`
6. Override login page template if needed via `our_brand/templates/includes/login/`.
7. Override email templates with our branding in `our_brand/templates/emails/`.
8. Install on site: `bench --site dev.local install-app our_brand`
9. Verify: no "Frappe" or "ERPNext" branding visible anywhere in the UI.

**IMPORTANT:** Keep all original GPLv3 license notices in the codebase. Only remove/replace visible product branding (logos, names, footer text), NOT license files or copyright headers in source code.

### Phase 3: Multi-Tenancy Configuration

1. Enable DNS-based multi-tenancy: `bench config dns_multitenant on`
2. Test: create a second site: `bench new-site client1.localhost`
3. Install apps on it: `bench --site client1.localhost install-app erpnext` then `install-app our_brand`
4. Verify both sites run independently on different domains with isolated databases.
5. Create a site provisioning script (`provision_client.sh`) that automates:
   - `bench new-site {domain}`
   - `bench --site {domain} install-app erpnext`
   - `bench --site {domain} install-app our_brand`
   - Set admin password
   - Run setup wizard via API or bench command
   - Configure site-specific branding (logo, colors) via `bench --site {domain} set-config`

### Phase 4: Per-Client Configuration System

Build into `our_brand` app a tenant configuration layer:

1. Create a DocType: **Tenant Settings** (single, per-site) with fields:
   - `tenant_name` (company name)
   - `logo` (attach image)
   - `primary_color` (color picker)
   - `secondary_color` (color picker)
   - `favicon` (attach image)
   - `login_background` (attach image)
   - `email_sender_name`
   - `email_footer_text`
   - `enabled_modules` (table/multi-select of available modules)
   - `custom_domain`
2. Write a Python hook that reads Tenant Settings on page load and injects the correct branding CSS dynamically.
3. Write a hook that shows/hides modules in the sidebar based on `enabled_modules`.
4. This allows per-client branding and module toggling without code changes.

### Phase 5: Module Configuration

ERPNext already ships these modules. Ensure each can be independently enabled/disabled per tenant:

- **CRM:** Leads, Opportunities, Customers, Sales Pipeline
- **Sales:** Quotations, Sales Orders, Sales Invoices
- **Purchasing:** Purchase Orders, Purchase Invoices, Suppliers
- **Finance/Accounting:** Chart of Accounts, General Ledger, GST, Payment Entries, Financial Statements
- **HR:** Employees, Attendance, Leave, Payroll
- **Inventory/Stock:** Items, Warehouses, Stock Entries, Stock Ledger
- **Projects:** Projects, Tasks, Timesheets, Gantt
- **Manufacturing:** BOM, Work Orders, Production Planning
- **Assets:** Asset Management, Depreciation
- **Support/Helpdesk:** Issues, SLA, Knowledge Base
- **Website:** CMS, Web Forms, Blog
- **Workflows:** Custom Workflows per DocType
- **Reports/Dashboards:** Report Builder, Query Reports, Dashboard Charts

For each module:
1. Verify it works independently when other modules are disabled.
2. Document inter-module dependencies (e.g., Sales needs Accounting).
3. Create module "presets" for common business types:
   - **Retail:** Stock + POS + Accounts + CRM
   - **Services:** Projects + CRM + HR + Accounts
   - **Manufacturing:** Manufacturing + Stock + Purchasing + Accounts
   - **General:** All modules enabled

### Phase 6: Production Deployment

1. Set up production server (Ubuntu 22.04, min 4GB RAM, 2 vCPU for starting).
2. `bench setup production {user}` → configures Nginx, Supervisor, Gunicorn.
3. Set up SSL per site: `bench setup lets-encrypt {site_name}`
4. Configure DNS: each client domain → server IP.
5. Set up automated backups:
   - `bench --site {site} backup` via cron (daily minimum)
   - Store backups offsite (S3 or equivalent)
6. Set up monitoring: uptime checks, disk/memory alerts.
7. Set up log rotation.
8. Firewall: allow only 80/443, restrict SSH.

### Phase 7: Client Onboarding Automation

Build a management command or admin panel in `our_brand`:

1. Admin inputs: client name, domain, admin email, selected modules, logo, colors.
2. Script runs: provisions site, installs apps, applies branding, enables modules, creates admin user, sends welcome email.
3. Total onboarding time target: under 10 minutes per client.

### Phase 8: Update & Maintenance Strategy

1. Track upstream Frappe/ERPNext releases.
2. Periodically merge upstream into our fork: `git fetch upstream && git merge upstream/version-15`
3. Resolve conflicts (our branding app is separate, so conflicts should be minimal).
4. Test on staging site before pushing to production.
5. `bench update` on production (with `--no-backup` only if backup already taken).
6. Roll out to all tenant sites at once.

---

## Architecture Summary

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

---

## Key Constraints

- **DO NOT** edit Frappe or ERPNext source for customizations. Use hooks, overrides, and the custom app.
- **DO NOT** delete GPLv3 license files or copyright headers from source.
- **DO** keep all customizations in `our_brand` app for clean upstream merges.
- **DO** test every upstream merge on a staging site before production.
- **DO** use Frappe's built-in RBAC, audit logs, API, and workflow engine — do not rebuild these.
- **DO** use Custom Fields and Custom DocTypes via UI for client-specific customizations rather than code.

---

## Success Criteria

- [ ] All Frappe/ERPNext branding replaced with ours
- [ ] Multi-tenant: 3+ sites running independently on one server
- [ ] Per-client branding (logo, colors, domain) configurable without code
- [ ] Modules toggleable per client
- [ ] New client provisionable in under 10 minutes
- [ ] Production: SSL, backups, monitoring in place
- [ ] Upstream updates mergeable without breaking customizations
