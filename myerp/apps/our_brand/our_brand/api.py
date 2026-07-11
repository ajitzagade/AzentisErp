import re

import frappe

from our_brand.utils import contrast_text_color, get_tenant_settings

# 6-digit only -- contrast_text_color()'s luminance calculation slices the
# string in 2-character pairs and would raise on 3-digit shorthand (#fff),
# which is exactly the kind of malformed-input crash AC2's fail-open
# requirement exists to prevent.
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


@frappe.whitelist(allow_guest=True)
def get_branding():
	"""Live per-tenant branding values for the runtime CSS-custom-property
	injection (Story 1.7, AD-3). Guest-accessible because the login page
	itself needs this before any authentication happens.

	Only truthy, valid values are included in the response -- omission
	(not a defaulted/null value) is the fail-open signal the frontend
	relies on: our_brand.css's own hardcoded :root defaults (Story 1.3)
	remain in effect for anything left out here, so a missing or
	malformed Tenant Settings record can never break page rendering.

	The whole body is wrapped in a catch-all: this is a guest-accessible
	endpoint the login page depends on, and AC2 requires it to fail open
	to stock/default branding rather than break the page -- an unhandled
	exception here would 500 the login page itself, which is exactly what
	fail-open means to avoid.
	"""
	try:
		tenant_settings = get_tenant_settings()

		branding = {}

		primary_color = tenant_settings.get("primary_color")
		secondary_color = tenant_settings.get("secondary_color")
		primary_valid = bool(HEX_COLOR_RE.match(primary_color or ""))
		secondary_valid = bool(HEX_COLOR_RE.match(secondary_color or ""))

		# Each color is independently valid/invalid -- a tenant who has only
		# set primary_color still gets that color live (AC1 doesn't require
		# both to be set together, they're two independent DocType fields).
		if primary_valid:
			branding["primary_color"] = primary_color
		if secondary_valid:
			branding["secondary_color"] = secondary_color
		if primary_valid and secondary_valid:
			branding["on_primary"] = contrast_text_color(primary_color, secondary_color)

		login_background = tenant_settings.get("login_background")
		if login_background:
			branding["login_background"] = login_background

		return branding
	except Exception:
		frappe.log_error(title="our_brand.api.get_branding failed open")
		return {}
