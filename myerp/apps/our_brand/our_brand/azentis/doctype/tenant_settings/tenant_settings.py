import frappe
from frappe.model.document import Document


class TenantSettings(Document):
	def validate(self):
		"""One seam for module-dependency warnings (AD-6): every save of
		Tenant Settings goes through this, whether triggered by a manual
		enabled_modules edit in the desk UI or by our_brand.module_rules.
		apply_preset()'s own save() call -- both flows reach
		validate_dependencies() this way, with no separate call site needed
		in either one.
		"""
		from our_brand.module_rules import validate_dependencies

		enabled = [row.module for row in (self.enabled_modules or [])]
		for warning in validate_dependencies(enabled):
			frappe.msgprint(warning, indicator="orange", title="Module Dependency Warning")
