import frappe


def after_install():
	"""Set platform-wide desk branding on install.

	hooks.py's app_title/app_logo_url alone are not reliable once more
	than 2 apps define app_logo_url (Frappe's own fallback logic in
	frappe.core.doctype.navbar_settings.navbar_settings.get_app_logo
	only special-cases exactly 2 apps) -- both frappe and erpnext define
	it, so with our_brand installed there are 3, and the desk chrome
	silently falls back to Frappe's own logo. The desk <title> tag has
	the same issue: it reads Website Settings.app_name (falling back to
	System Settings, then hardcoded "Frappe"), never hooks.py's
	app_title. Website Settings is the authoritative source for both;
	set it directly here so branding actually appears, not just exists
	in hooks.py.
	"""
	website_settings = frappe.get_single("Website Settings")
	website_settings.app_name = "Azentis"
	website_settings.app_logo = "/assets/our_brand/images/logo.png"
	website_settings.splash_image = "/assets/our_brand/images/logo.png"
	website_settings.save(ignore_permissions=True)

	create_default_email_account()

	from our_brand.module_rules import seed_module_presets

	seed_module_presets()


def create_default_email_account():
	"""Make the Email Account record's own name the visible sender identity
	for system-triggered emails (password reset, welcome), instead of
	Frappe's hardcoded "Notifications" dummy fallback.

	frappe.core.doctype.user.user.User.send_login_mail() passes sender=None
	for Administrator/Guest-triggered emails (the common case for these
	flows), which falls through to
	EmailAccount.find_default_outgoing() -> find_from_config() (nothing in
	site config) -> create_dummy(), hardcoded in Frappe core to
	{"name": "Notifications", "email_id": "notifications@example.com"} --
	not overridable via hooks. The only real fix is to make a genuine
	default outgoing Email Account exist first, so find_one_by_filters()
	finds it before ever reaching that hardcoded fallback.

	awaiting_password=1 independently short-circuits
	EmailAccount.validate()'s live-SMTP-connection-test block (see
	validate(), the `not self.awaiting_password` guard) -- safe to create
	without real SMTP credentials, which platform branding has no business
	owning; real SMTP provisioning is a later-epic infrastructure concern.
	always_use_account_name_as_sender_name=1 is what actually forces this
	account's name to be used as the sender display name even when a
	session-user-based sender was otherwise computed
	(email_body.py::replace_sender_name()).
	"""
	if frappe.db.exists("Email Account", "Azentis"):
		return

	email_account = frappe.new_doc("Email Account")
	email_account.email_account_name = "Azentis"
	email_account.email_id = "no-reply@azentis.local"
	email_account.enable_outgoing = 1
	email_account.default_outgoing = 1
	email_account.awaiting_password = 1
	email_account.always_use_account_name_as_sender_name = 1
	email_account.insert(ignore_permissions=True)


def before_uninstall():
	"""Restore stock branding on uninstall, so AC3's isolation check
	(stock Frappe/ERPNext branding returns cleanly) actually holds --
	otherwise Website Settings would keep our values after our_brand is
	gone, which is exactly the kind of leftover state AC3 is checking
	for.
	"""
	website_settings = frappe.get_single("Website Settings")
	website_settings.app_name = None
	website_settings.app_logo = None
	website_settings.splash_image = None
	website_settings.save(ignore_permissions=True)

	if frappe.db.exists("Email Account", "Azentis"):
		frappe.delete_doc("Email Account", "Azentis", ignore_permissions=True, force=True)

	from our_brand.module_rules import MODULE_PRESETS

	for preset_name in MODULE_PRESETS:
		if frappe.db.exists("Module Preset", preset_name):
			frappe.delete_doc("Module Preset", preset_name, ignore_permissions=True, force=True)
