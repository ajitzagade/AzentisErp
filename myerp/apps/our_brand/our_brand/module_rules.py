import frappe

# The curated set of business modules a tenant can toggle in the sidebar.
# Deliberately excludes Frappe's own system-level modules (Core, Custom,
# Desk, Email, Workflow, Automation, Printing, Social, Geo, Integrations,
# Contacts, Website) and ERPNext's niche/setup-oriented ones (Bulk
# Transaction, Communication, EDI, ERPNext Integrations, Maintenance,
# Portal, Quality Management, Regional, Setup, Subcontracting, Telephony,
# Utilities) -- none of those are business-facing sidebar sections an SMB
# tenant would think of as a toggleable "module". POS folds into Accounts
# (POS Invoice/POS Profile both belong to that module in this ERPNext
# version, confirmed via frappe.db.get_value). No HR module exists in this
# stack -- ERPNext v15+ split HR/Payroll into a separate hrms app, not part
# of this project's pinned stack (see Story 3.1's Dev Notes).
TOGGLEABLE_MODULES = [
	"CRM",
	"Selling",
	"Buying",
	"Accounts",
	"Stock",
	"Projects",
	"Manufacturing",
	"Assets",
	"Support",
]


def sync_blocked_modules(doc, method=None):
	"""Sync every System User's block_modules from Tenant Settings.enabled_modules.

	Frappe's own sidebar/desktop-icon rendering (frappe.desk.desktop.
	get_workspace_sidebar_items, frappe.desk.doctype.desktop_icon) already
	filters by User.block_modules -- this is nav-level only, never wired
	into Role Permissions or route/API access anywhere in Frappe core, which
	is exactly AD-4's "navigation-level, not a security boundary" behavior,
	for free. This function's only job is keeping block_modules in sync with
	the tenant's own enabled_modules choice.

	Users with a Module Profile assigned are skipped, not overwritten. Frappe's
	own User.validate() -> validate_allowed_modules() unconditionally
	re-derives block_modules from the linked Module Profile on every
	User.save() -- including the save() this function itself issues -- so a
	write here would be silently discarded for those users regardless (this
	was confirmed by two independent code-review passes reproducing it
	empirically, not theorized). Module Profile is Frappe's own, separate
	module-blocking mechanism; for a user who has one assigned, it is already
	the authoritative source and this function correctly defers to it rather
	than fighting a Frappe core validation hook (which AD-1 forbids touching).
	"""
	enabled = {row.module for row in (doc.enabled_modules or [])}

	if enabled:
		blocked = [m for m in TOGGLEABLE_MODULES if m not in enabled]
	else:
		# Fail open: no enabled_modules set yet means show everything.
		blocked = []

	users = frappe.get_all(
		"User",
		filters={"user_type": "System User", "enabled": 1, "module_profile": ["in", ["", None]]},
		pluck="name",
	)
	for user in users:
		user_doc = frappe.get_doc("User", user)
		user_doc.set("block_modules", [{"module": module} for module in blocked])
		user_doc.save(ignore_permissions=True)


# Business-type presets, per the PRD addendum's table. Two compositions
# deviate from the addendum's literal wording, both documented in Story
# 3.4's Dev Notes: Retail's "POS" folds into Accounts (no separate POS
# Module Def exists), and Services omits "HR" entirely (no HR Module Def
# exists in this stack -- ERPNext v15+ split it into a separate hrms app).
# "Purchasing" -> Buying and "Manufacturing"/"Stock"/"CRM"/"Projects"/
# "Accounts" are exact ERPNext Module Def names.
MODULE_PRESETS = {
	"Retail": ["Stock", "Accounts", "CRM"],
	"Services": ["Projects", "CRM", "Accounts"],
	"Manufacturing": ["Manufacturing", "Stock", "Buying", "Accounts"],
	"General": list(TOGGLEABLE_MODULES),
}


def seed_module_presets():
	"""Create the 4 named Module Preset records if they don't already exist.

	Idempotent -- safe to call on every install (a new site's after_install)
	and to re-run manually without duplicating or erroring, including if two
	callers race and both pass the exists() check before either inserts.
	"""
	for preset_name, modules in MODULE_PRESETS.items():
		if frappe.db.exists("Module Preset", preset_name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Module Preset",
				"preset_name": preset_name,
				"modules": [{"module": module} for module in modules],
			}
		)
		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError:
			pass


@frappe.whitelist()
def apply_preset(preset_name):
	"""Copy a Module Preset's module list into the current site's Tenant
	Settings.enabled_modules as a snapshot -- not a live reference back to
	the preset (AD-5). Building fresh {"module": ...} dicts here, rather than
	reusing the preset's own child-row objects, is what makes this a
	snapshot: editing the preset afterward never retroactively changes an
	already-onboarded tenant, since the copied rows now belong solely to
	this site's own Tenant Settings document.

	Saving Tenant Settings re-triggers sync_blocked_modules (Story 3.2) as a
	normal side effect of its on_update hook -- applying a preset updates
	the live sidebar immediately, no separate step needed.

	Whitelisted (not console-only) so this is an actually-usable action, per
	AC2's own wording ("when the action runs") -- restricted to System
	Manager since it mutates tenant-wide module config and cascades into a
	write on every System User via sync_blocked_modules.
	"""
	if "System Manager" not in frappe.get_roles():
		frappe.throw(frappe._("Only a System Manager can apply a module preset."), frappe.PermissionError)

	if not frappe.db.exists("Module Preset", preset_name):
		frappe.throw(frappe._("Unknown module preset: {0}").format(preset_name))

	preset = frappe.get_doc("Module Preset", preset_name)
	tenant_settings = frappe.get_doc("Tenant Settings")
	tenant_settings.set("enabled_modules", [{"module": row.module} for row in preset.modules])
	tenant_settings.save(ignore_permissions=True)


# Conservative, deliberately non-exhaustive: only dependencies with a clear,
# real functional basis in ERPNext. Data, not code -- extending this map
# later is a data change, not a re-architecture (AD-5/AD-6's framing).
MODULE_DEPENDENCIES = {
	"Selling": ["Accounts"],  # Sales Invoice is fundamentally an accounting document
	"Buying": ["Accounts"],  # Purchase Invoice, same reasoning
	"Manufacturing": ["Stock"],  # BOMs/Work Orders operate on Stock items
}


def validate_dependencies(enabled_modules):
	"""Pure function: given a list of enabled module names, return a list of
	warning strings for any module whose declared dependency isn't also
	enabled. Never raises -- warn-only, per PRD section 10.6. The one and only
	dependency-checking logic in the codebase (AD-6) -- callers (Tenant
	Settings' own validate()) are responsible for surfacing these, not for
	deciding what counts as a violation.
	"""
	enabled = set(enabled_modules)
	warnings = []
	for module, required in MODULE_DEPENDENCIES.items():
		if module not in enabled:
			continue
		for dependency in required:
			if dependency not in enabled:
				warnings.append(f"{module} is enabled but requires {dependency}, which is not enabled.")
	return warnings
