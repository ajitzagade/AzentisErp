// Bounded-timeout fallback for the branded splash screen (Story 1.4, AC3).
// Frappe's own desk.js removes .splash once the desk UI finishes loading
// (make_page_container() -> $(".splash").remove()); if that hasn't happened
// within SPLASH_TIMEOUT_MS, .splash is still in the DOM and we show a
// retry state instead of leaving the spinner running forever.
(function () {
	var SPLASH_TIMEOUT_MS = 15000;

	setTimeout(function () {
		var splash = document.querySelector(".splash");
		if (!splash) {
			return;
		}
		var spinner = splash.querySelector(".azentis-splash-spinner");
		var retry = splash.querySelector(".azentis-splash-retry");
		if (spinner) {
			spinner.style.display = "none";
		}
		if (retry) {
			retry.style.display = "block";
		}
	}, SPLASH_TIMEOUT_MS);
})();
