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
	website_settings.save(ignore_permissions=True)


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
	website_settings.save(ignore_permissions=True)
