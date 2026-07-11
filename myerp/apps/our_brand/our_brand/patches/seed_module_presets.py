from our_brand.module_rules import seed_module_presets


def execute():
	"""Backfill the 4 named Module Preset records on every site, not just
	freshly-installed ones. after_install() alone only reaches sites created
	after this code existed -- a site provisioned earlier (Story 2.2's
	acme.dev.local, before Story 3.4 shipped) drifted out of sync and had to
	be fixed by hand. This patch runs on every `bench migrate`, so future
	preset additions/changes to MODULE_PRESETS backfill automatically instead
	of relying on someone remembering to re-run seed_module_presets() by hand.
	"""
	seed_module_presets()
