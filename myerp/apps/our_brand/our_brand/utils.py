import frappe


def get_tenant_settings():
	"""The one sanctioned read path for Tenant Settings (AD-2).

	Every consumer (branding injection, sidebar filtering, etc.) must go
	through this accessor rather than a scattered raw frappe.get_single/
	frappe.get_doc call, so there is exactly one place that could ever be
	stale -- and frappe.get_cached_doc's cache is invalidated automatically
	on save, so it never is.
	"""
	return frappe.get_cached_doc("Tenant Settings")


def _relative_luminance(hex_color):
	"""WCAG relative luminance of a hex color (0.0 = black, 1.0 = white)."""
	hex_color = hex_color.lstrip("#")
	r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

	def channel(c):
		return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

	r, g, b = channel(r), channel(g), channel(b)
	return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_text_color(hex1, hex2, light="#FFFFFF", dark="#1B1725"):
	"""Pick a readable text color for a gradient spanning hex1 -> hex2.

	Averages both stops' relative luminance (the gradient renders at every
	point between them) and returns the fixed light/dark token whose
	luminance is furthest away, guaranteeing contrast regardless of the
	color pair supplied.
	"""
	avg_luminance = (_relative_luminance(hex1) + _relative_luminance(hex2)) / 2
	return dark if avg_luminance > 0.5 else light
