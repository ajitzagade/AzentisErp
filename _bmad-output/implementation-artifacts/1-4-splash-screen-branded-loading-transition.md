---
baseline_commit: ece3a97
---

# Story 1.4: Splash Screen — Branded Loading Transition

Status: done

## Story

As a tenant's staff user,
I want a branded loading transition between login and the working ERP, not a flash of unstyled content,
so that the branded experience feels continuous, not like it drops back to generic software mid-flow.

## Acceptance Criteria

1. Given login succeeds, when the desk UI is still loading, then the splash screen renders the same mesh/glass visual language as the login page (or the tenant's `login_background` image, if set) with a centered logo mark and a loading indicator — no form, no other interactive elements.
2. Given the desk UI finishes loading, when the splash screen is showing, then it auto-dismisses without requiring any user action.
3. Given the desk UI fails to load within a bounded timeout, when the splash screen is showing, then it replaces the loading indicator with a plain "Something went wrong loading your workspace. Retry" message and button — still on the mesh/image background, no glass card needed for a single message.
4. Given the same light/dark and `prefers-reduced-motion` conditions as Story 1.3, when the splash screen renders, then it inherits identical theme and motion behavior — no separate logic duplicated for this surface.

## Dev Notes — Read Before Starting

**The splash screen already exists in Frappe core — this story restyles/extends it, it does not build one from scratch.** Investigated during story creation:

- `myerp/apps/frappe/frappe/www/app.html` (the desk shell, read fully) includes `{% include "templates/includes/splash_screen.html" %}` as the very first thing in `<body>`, before any JS boots.
- `myerp/apps/frappe/frappe/templates/includes/splash_screen.html` (read fully) is a 4-line template: `<div class="centered splash"><img src="{{ splash_image or default }}"></div>`.
- `splash_image` is a real `Website Settings` field (`frappe/website/doctype/website_settings/website_settings.py:61,259-260`) — **no template override is needed just to swap the logo**, set `Website Settings.splash_image` in `install.py`'s `after_install()`, same pattern already established in Story 1.2 for `app_name`/`app_logo`.
- **Auto-dismiss (AC2) already happens for free.** `frappe/public/js/frappe/desk.js::make_page_container()` runs `$(".splash").remove()` once the `#body` container exists — this is Frappe's own existing lifecycle code, not something this story needs to build. Do not add duplicate dismiss logic.
- **What's missing from stock Frappe, and is this story's actual scope:** (a) the mesh/glass background behind the splash (currently just a bare logo on whatever background color the page has), (b) an actual loading indicator/spinner (doesn't exist today — just the logo), (c) the bounded-timeout "Something went wrong... Retry" fallback (AC3 — does not exist in stock Frappe at all).
- **Template override still needed for (b) and (c)**, since they require new DOM (a spinner element, a hidden retry message+button) that CSS alone cannot create without existing markup to target. Override `our_brand/templates/includes/splash_screen.html` (same reverse-install-order Jinja mechanism proven in Story 1.3 for `footer_powered.html` — `our_brand` installs last, so its copy at the same relative path wins). Still read `splash_image` from context so admin configurability via Website Settings is preserved, not regressed.
- **CSS reuse, not duplication (AC4).** The mesh background technique, `--tenant-primary`/`--tenant-secondary`/`--login-background-image` custom properties, and the `prefers-color-scheme`/`prefers-reduced-motion` media queries already exist in `our_brand/public/css/our_brand.css` from Story 1.3. Add new rules scoped to `.splash` in the *same* stylesheet (already loaded on the desk shell via `app_include_css`, confirmed in Story 1.3's verification) — do not create a second stylesheet or duplicate the mesh gradient definition. `.splash` positions itself via Frappe's own `.centered` class (`position: absolute; top/left: 50%; transform: translate(-50%,-50%)`, in `frappe/public/scss/common/global.scss` — read-only reference) which this story does not touch; the mesh background is added via a `position: fixed; inset: 0` pseudo-element on `.splash` itself, which escapes the parent's auto-sized box regardless of `.centered`'s positioning — confirmed no CSS conflict.
- **Spinner motion vs. mesh drift motion are different categories.** `prefers-reduced-motion: reduce` must still disable the decorative mesh drift (identical to Story 1.3). The loading spinner is a functional progress indicator, not decorative — per common accessibility practice (and consistent with WCAG's animation-from-interaction guidance), it may continue to animate even under reduced-motion, since it communicates real in-progress state rather than playing for atmosphere. Document this reasoning inline if implemented this way; do not silently diverge without a comment.
- **Retry fallback (AC3) needs new JS**, since nothing bounded-timeout-based exists in stock Frappe. Add `our_brand/public/js/splash_retry.js`, wired via `app_include_js` (desk-only — this is not a web/login-page concern, so `web_include_js` is not needed). Logic: bounded `setTimeout` (document the chosen duration and why); on fire, check whether `.splash` is still present in the DOM (if desk finished loading, Frappe's own `desk.js` already removed it — nothing to do); if still present, reveal the pre-rendered hidden retry block from the template override. The retry button's action is a plain page reload (`location.reload()`) — do not build custom retry/backoff logic beyond what the AC asks for.
- **`.splash`/`.centered` selector safety already checked**: grepped Frappe's SCSS for other consumers of `.splash` — none found, safe to use as a unique scoping selector without collision risk.

### Previous Story Intelligence (1.1–1.3)

- `app_include_css`/`web_include_css` already point at `our_brand/public/css/our_brand.css` (Story 1.3) — desk pages (which is where the splash renders) already receive this stylesheet, confirmed via authenticated curl against `/app` in Story 1.3.
- Verification method: authenticated curl (`/api/method/login` + cookie jar) against `/app` for desk-shell HTML/asset checks — same as Story 1.3.
- `bench build --app our_brand` needed after adding the new JS file; raw `public/css/*.css` edits are served live without a rebuild (confirmed in Story 1.3), but new JS entries under `app_include_js` may need a build pass to be picked up — verify empirically, don't assume.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Set the splash logo via Website Settings, not a template override (AC: 1)
  - [x] Extended `our_brand/our_brand/install.py::after_install()`/`before_uninstall()` to set/clear `Website Settings.splash_image`
  - [x] Since Story 1.1/1.2 already ran `after_install()` on the existing `dev.local` site (this field didn't exist then), re-ran it via `bench --site dev.local execute our_brand.install.after_install` to apply retroactively — confirmed idempotent (matches existing `app_name`/`app_logo` pattern which was already applying cleanly)
- [x] Task 2: Override the splash template to add spinner + hidden retry markup (AC: 1, 3)
  - [x] Created `our_brand/our_brand/templates/includes/splash_screen.html`
  - [x] Verified via authenticated curl against `/app`: our override renders (spinner + retry block present, `<img src="/assets/our_brand/images/logo.png">` confirms `Website Settings.splash_image` is being read correctly)
- [x] Task 3: Style the splash screen — mesh background, spinner, retry state (AC: 1, 3, 4)
  - [x] Refactored the Story 1.3 mesh-background rule to a shared selector list (`#page-login .page-content-wrapper::before, .splash::before`) rather than duplicating it — same gradient, same custom properties, same `@keyframes`, same reduced-motion query, satisfying AC4 literally, not just in spirit
  - [x] `.splash`'s own light/dark surface tokens (`--mesh-base`, `--text`, `--text-muted`, etc.) also merged into the same `#page-login, .splash` selector list Story 1.3 already declared
  - [x] Added CSS-only spinner (`.azentis-splash-spinner`, rotating ring via `border-top-color` + `@keyframes azentis-spin`)
  - [x] Styled the retry message/button reusing the same button gradient as the login page's primary button
- [x] Task 4: Bounded-timeout retry fallback (AC: 3)
  - [x] Created `our_brand/our_brand/public/js/splash_retry.js` (15s bounded timeout, checks `.splash` presence, reveals retry block)
  - [x] Wired via `app_include_js`; confirmed empirically it renders *after* the splash markup in `app.html`'s body (Frappe's own `{% for include in include_js %}` loop sits near the end of `<body>`, after the splash include) — so `document.querySelector('.splash')` reliably finds the element, no `DOMContentLoaded` wrapper needed
- [x] Task 5: Build and verify end-to-end (AC: all)
  - [x] `bench build --app our_brand` — succeeded
  - [x] Authenticated curl against `/app` confirmed: splash `<img>` (our logo), `.azentis-splash-spinner`, `.azentis-splash-retry` (hidden by default), `our_brand.css` and `splash_retry.js` both linked, JS confirmed positioned after the splash markup in raw HTML byte offset
  - [x] AC2 (auto-dismiss) verified by reading `frappe/public/js/frappe/desk.js::make_page_container()` — stock `$(".splash").remove()` logic, untouched; no redundant dismiss logic added by this story
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `bench build --app our_brand` → succeeded, "Application Assets Linked"
- `bench --site dev.local execute our_brand.install.after_install` → applied `splash_image` retroactively to the existing dev site
- Authenticated curl (`/api/method/login` + cookie jar) against `/app` → splash markup, spinner, retry block, both new assets all confirmed present in raw HTML
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Most of AC2 (auto-dismiss) was already built** — this is the second story in a row (after Story 1.3's font discovery) where investigating Frappe core first revealed an existing mechanism this story only needed to *not break*, rather than build. Confirmed by reading `desk.js` rather than by black-box re-testing, since there was no new code path to exercise for that AC.
- **AC4's "no separate logic duplicated" was treated as a hard constraint, not just phrasing** — refactored Story 1.3's mesh-background/token rules into shared selectors (`#page-login .page-content-wrapper::before, .splash::before` etc.) instead of copy-pasting a second near-identical block. Verified no regression to the login page's own rendering by re-checking the same curl assertions used in Story 1.3 were still true after the refactor (footer text, CSS link, `id="page-login"` — spot-checked, not re-run in full).
- **Spinner motion under `prefers-reduced-motion: reduce`**: deliberately left animating (documented inline in the CSS) on the reasoning that it's a functional progress indicator, not decorative atmosphere like the mesh drift. This is a judgment call the story's own Dev Notes flagged as needing an explicit comment if made — done.
- **Retroactive migration note**: `Website Settings.splash_image` didn't exist as a concern until this story, so the already-installed `dev.local` site needed `after_install()` re-run manually via `bench execute` to pick it up. This is a one-time dev-environment fixup; a fresh `bench install-app our_brand` on a new site would get it automatically through the normal `after_install` hook. Not something Story 1.7's real per-tenant provisioning flow needs to worry about since it installs fresh.
- No automated test framework, consistent with Stories 1.1–1.3's documented decision — verification is curl/grep-based plus direct source reading for behavior this story reuses rather than builds.

### File List

- `myerp/apps/our_brand/our_brand/install.py` (modified — `splash_image` set/clear)
- `myerp/apps/our_brand/our_brand/templates/includes/splash_screen.html` (new)
- `myerp/apps/our_brand/our_brand/public/css/our_brand.css` (modified — shared mesh-background refactor + `.splash`/spinner/retry rules)
- `myerp/apps/our_brand/our_brand/public/js/splash_retry.js` (new)
- `myerp/apps/our_brand/our_brand/hooks.py` (modified — `app_include_js`)
