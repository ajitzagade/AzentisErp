// Live per-tenant branding injection (Story 1.7, AD-3). Fetches the current
// tenant's colors/login_background and sets them as inline CSS custom
// properties on <html> -- our_brand.css's own hardcoded :root defaults
// (Story 1.3) stay in effect for anything this doesn't set, which is the
// fail-open behavior AC2 asks for: no explicit error handling needs to
// duplicate those defaults, absence alone is enough.
(function () {
	var PROPERTY_MAP = {
		primary_color: "--tenant-primary",
		secondary_color: "--tenant-secondary",
		on_primary: "--tenant-on-primary",
	};

	fetch("/api/method/our_brand.api.get_branding", { credentials: "same-origin" })
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			var branding = (data && data.message) || {};
			var root = document.documentElement.style;

			Object.keys(PROPERTY_MAP).forEach(function (key) {
				if (branding[key]) {
					root.setProperty(PROPERTY_MAP[key], branding[key]);
				}
			});

			if (branding.login_background) {
				// Escape backslashes/quotes before embedding in a CSS url("...")
				// string token -- login_background is server-validated as
				// truthy only, not format-checked, so treat it as untrusted
				// text here rather than assuming it's already CSS-safe.
				var escaped = String(branding.login_background).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
				root.setProperty("--login-background-image", 'url("' + escaped + '")');
			}
		})
		.catch(function () {
			// Silently fail open -- our_brand.css's platform defaults apply.
		});
})();
