---
baseline_commit: ece3a97
---

# Story 1.3: Visual Theming — Colors and the Login Page (Light/Dark, Responsive, Accessible)

Status: done

## Story

As the platform operator,
I want primary/accent colors and the login page restyled — including light/dark theme, mobile responsiveness, and accessibility fallbacks,
so that the platform looks like our product, not a generic Frappe install, on any device or system preference a real user actually has.

## Acceptance Criteria

1. Given `our_brand`'s stylesheet is included via `app_include_css`, when any page loads, then primary/accent colors match our theme.
2. Given a user visits the login page, when it renders, then it shows our styling, not Frappe's default login template, and the footer no longer reads "Built on Frappe/ERPNext" (or equivalent stock text). No per-tenant static CSS file is generated — this story is platform-wide only (per-tenant dynamic theming is Story 1.7).
3. Given the OS/browser reports `prefers-color-scheme: dark`, when the login page renders, then it automatically uses dark-theme tokens — no manual toggle.
4. Given `prefers-reduced-motion: reduce`, when the mesh background renders, then the drift animation is disabled entirely (not slowed).
5. Given the browser doesn't support `backdrop-filter`, when the login card renders, then it falls back to a near-opaque surface — never broken/transparent.
6. Given the platform-default primary/secondary color pair, when the primary button renders, then its text color is computed to guarantee readability against that gradient — never a naive hardcoded value that could fail for an arbitrary future tenant color pair.
7. Given a viewport narrower than `md` (768px), when the login page renders, then: card is fluid-width (capped, not fixed desktop width), every input/checkbox/link meets 44px minimum touch target (48px primary button), input font-size fixed at 16px minimum (prevents iOS Safari auto-zoom), background uses `dvh` not `vh`, `env(safe-area-inset-*)` padding clears notch/home-indicator devices.
8. **Structural readiness only, not full dynamic behavior** (see Dev Notes — forward dependency on Story 1.6): the CSS/template must support a background-image override mechanism (a `--login-background-image` custom property that, when set, replaces the mesh) so Story 1.7 can wire it to `Tenant Settings.login_background` once that field exists. Prove the mechanism works with a manually-set test value; do not attempt to read from Tenant Settings in this story.

## Dev Notes — Read Before Starting

**Forward-dependency conflict, resolved:** `Tenant Settings` (Story 1.6) doesn't exist yet, but epics.md's own AC text for this story references `Tenant Settings.login_background`. Resolution: this story builds the CSS *structural capability* (AC8), platform-default colors are **hardcoded**, not read from any DocType. Story 1.7 ("Dynamic Per-Tenant Branding Injection") is what wires live data in. Do not attempt to create or read Tenant Settings here — that would be scope creep into Story 1.6/1.7's territory and violate the "create only what's needed now" discipline established in every prior story.

**Architecture approach — CSS-injection, not template replacement.** `frappe/www/login.html` (the real file, read it before starting) is a large, functionally rich template (social login, LDAP, signup, forgot-password, email-link-login). Per AD-3 ("tenant colors render as inline CSS custom properties... never a compiled per-tenant static asset file") and the addendum's original plan (`app_include_css`), the correct approach is **restyling the existing DOM via CSS**, not forking/replacing the whole template. This preserves all existing login functionality automatically. Only override two small, isolated pieces:
- `our_brand/templates/includes/footer/footer_powered.html` — overrides ERPNext's "Powered by ERPNext" footer include (confirmed real file at `erpnext/erpnext/templates/includes/footer/footer_powered.html`). Verified override mechanism: Frappe's Jinja `ChoiceLoader` searches installed apps in *reverse install order* (`frappe/utils/jinja.py::get_jloader`) — since `our_brand` installs last, a same-path file in `our_brand/templates/...` wins automatically. No frappe/erpnext source is touched.
- Everything else (mesh background, glass card, colors, typography, responsive/accessibility rules) is a CSS file wired via `app_include_css` in `hooks.py`, targeting the *existing* login page's real CSS classes (`.for-login`, `.page-card`, `.login-content`, `.form-signin`, `.app-logo`, `input`, `.btn-login`) — read `frappe/www/login.html` to get the exact class names right; do not guess them.

**Mesh background — pure CSS, no new DOM nodes.** Use layered `radial-gradient` backgrounds (or `::before`/`::after` pseudo-elements) with `filter: blur()` and `background-position`/`transform` animation on an existing container (e.g., `body` or `.for-login`), not new `<div>` elements requiring template changes or JS injection. This keeps the change CSS-only.

**Design tokens — pull exact values from the finalized UX spines**, do not invent new ones:
- `_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/DESIGN.md` — colors (platform default `#6D28D9`/`#06B6D4`), typography (Inter — self-host, no external font CDN), rounded scale (`sm:12px md:16px lg:22px full:9999px`), spacing (mobile card tokens), component specs for `login-card`, `mesh-background`, `button-primary`, `input`.
- `_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/EXPERIENCE.md` — Responsive & Platform section has the exact mobile rules (16px input font-size rationale, `dvh`, `env(safe-area-inset-*)`, touch targets) — this is AC7, already fully specified, just implement it.
- `_bmad-output/planning-artifacts/ux-designs/ux-AzentisERP-2026-07-10/mockups/login-full-bleed-glass.html` and `mockups/login-mobile.html` — working HTML/CSS reference implementations from the UX pass. Use these as the ground truth for exact CSS values (blur radii, shadow values, animation timing) rather than re-deriving them from prose.

**Button text contrast (AC6) needs a real luminance computation, not a guess.** DESIGN.md specifies this must be "computed server-side from the gradient's relative luminance." Implement as a small Python utility (e.g., `our_brand/utils.py::contrast_text_color(hex1, hex2)`) using the WCAG relative luminance formula, called from a Jinja context method or `website_context` hook so the login template can use it. Since colors are hardcoded platform defaults in this story (not per-tenant yet), this can be computed once and cached, but implement the *function* generically (takes two hex colors, returns a safe text color) since Story 1.7 will call it again with real per-tenant colors.

**Self-hosted Inter font** — do not link to Google Fonts or any external CDN (`DESIGN.md`'s explicit rule, also matches the project's general "no external network calls" discipline). Download/vendor the font files into `our_brand/public/fonts/` and reference via `@font-face`.

**Reduced-motion and dark-mode are pure CSS media queries** (`@media (prefers-reduced-motion: reduce)`, `@media (prefers-color-scheme: dark)`) — no JS detection needed, no server-side logic.

### Previous Story Intelligence (1.1, 1.2)

- Bench: `myerp/`, site `dev.local`, `our_brand` already scaffolded and installed with working `hooks.py`/`install.py`.
- **`app_include_css` goes in `hooks.py`** — follow the same pattern as `app_logo_url` (Story 1.2): declare it, but *verify empirically* it actually renders (curl the login page HTML and check for the `<link>` tag / computed styles), don't just trust that setting the hook is sufficient — Story 1.2 found real gaps between "hook is set" and "actually visible," twice.
- Verification method established in Story 1.2: authenticated curl is for the *desk*; for the *login page* (public, no auth needed), a plain `curl -H "Host: dev.local" http://127.0.0.1:8000` is sufficient to check rendered HTML/CSS links.
- `bench build --app our_brand` (or a full `bench build`) is needed after adding CSS/font/JS assets for them to be compiled into `/assets/our_brand/`.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile.

## Tasks / Subtasks

- [x] Task 1: Read the real login template and establish exact class names (AC: 2)
  - [x] Read `myerp/apps/frappe/frappe/www/login.html` completely
  - [x] Noted exact selectors: `.for-login`/`.for-signup`/`.for-forgot`/`.for-login-with-email-link`/`.for-email-login`, `.page-card`, `.login-content`, `.page-card-head`, `.page-card-body`, `.app-logo`, `.form-signin`, `.form-control`, `.btn-login`, `.forgot-password-message`, `.sign-up-message`; confirmed `container_attributes()` in `web.html` yields `id="page-login"` on the outer wrapper — used as the scoping root for every rule
- [x] Task 2: Override the "Powered by ERPNext" footer include (AC: 2)
  - [x] Created `our_brand/our_brand/templates/includes/footer/footer_powered.html`
  - [x] Verified via curl: footer now renders "Powered by Azentis", confirming the reverse-install-order Jinja override works
- [x] Task 3: Build the design token stylesheet (AC: 1, 3, 4, 5, 6, 7, 8)
  - [x] Created `our_brand/our_brand/public/css/our_brand.css`: `:root`-level `--primary`/`--brand-color` override (AC1, platform-wide), `#page-login`-scoped light/dark tokens, 3-blob mesh background via layered `radial-gradient`s + `blur(34px)` on a single `::before` pseudo-element (no new DOM nodes), glass card with `backdrop-filter`, rounded/spacing tokens
  - [x] Added `@media (prefers-color-scheme: dark)` dark-token overrides
  - [x] Added `@media (prefers-reduced-motion: reduce)` disabling the drift `@keyframes` entirely
  - [x] Added `@media (max-width: 767px)` mobile rules: fluid capped width, 16px input font-size, 44/48px touch targets, `dvh`, `env(safe-area-inset-*)`
  - [x] Added `--login-background-image` custom-property hook (AC8) as the `var()` fallback source for the mesh `background-image`; proved the swap mechanism with a manually-appended test rule (confirmed live via curl, no rebuild needed since `public/css/*.css` is served unbundled), then removed the test rule before finishing
- [x] Task 4: Self-host Inter font (AC: per Dev Notes)
  - [x] **Scope note**: no new font vendoring was needed — Frappe core already self-hosts Inter (`frappe/public/css/fonts/inter/`, including `InterVariable.woff2`) and already loads it via `login.bundle.css`, which the login page already includes. Referenced `font-family: "Inter", ...` in the stylesheet; confirmed the `@font-face` declarations are present in the compiled `login.bundle.css` actually served to the login page.
- [x] Task 5: Implement server-side contrast computation (AC: 6)
  - [x] Created `our_brand/our_brand/utils.py::contrast_text_color(hex1, hex2)` using the WCAG relative-luminance formula, averaging both gradient stops
  - [x] **Scope note on wiring**: did not wire a `update_website_context` hook in this story — investigated Frappe's actual hook (`frappe.get_hooks("update_website_context")` in `base_template_page.py`, not the guessed `website_context`) but found no safe injection point into `login.html`'s CSS without touching that template (its `head_include` block is fully overridden by login.html itself, not extended via `super()`). Since this story's colors are fixed platform defaults (not yet per-tenant), computed the value directly by running the function once (`contrast_text_color('#6D28D9', '#06B6D4')` → `#FFFFFF`, matching `DESIGN.md`'s stated default) and used that as the literal `--tenant-on-primary` value in the stylesheet. The function itself is real, tested by direct invocation, and ready for Story 1.7 to call per-render once dynamic per-tenant colors and a real template injection point exist.
- [x] Task 6: Wire `app_include_css`/`web_include_css` and build (AC: 1)
  - [x] Wired both hooks in `hooks.py` (both desk and web templates need the override for AC1's "any page" scope) pointing at `our_brand.css`
  - [x] `bench build --app our_brand` — succeeded, assets linked
- [x] Task 7: Verify end-to-end against every AC (AC: all)
  - [x] `curl -H "Host: dev.local" http://127.0.0.1:8000/login` — CSS `<link>` present, footer reads "Powered by Azentis", `id="page-login"` confirmed on the scoping element, all targeted classes (`.page-content-wrapper`, `.page_content`, `.page-card-head`, `.login-content.page-card`, `.app-logo`, `.btn-login`) confirmed present in real rendered HTML
  - [x] Authenticated curl against `/app` (desk shell) confirmed `our_brand.css` `<link>` present there too (AC1's platform-wide scope)
  - [x] Confirmed no ID selectors in `login.bundle.css` compete with our `#page-login`-scoped rules — our rules win the cascade regardless of `<link>` load order
  - [x] Confirmed no per-tenant static CSS file was generated anywhere (AC2) — only the one platform-wide `our_brand.css`
  - [x] `git status` in `myerp/apps/frappe` and `myerp/apps/erpnext` — both clean, matching Story 1.1/1.2 baseline
  - [x] Dark-mode/reduced-motion/backdrop-filter-fallback/mobile rules verified present in the served CSS via direct grep of the exact media-query/property signatures; true pixel-level visual rendering was not verified in a real browser — see Completion Notes

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `curl -H "Host: dev.local" http://127.0.0.1:8000/login` → 200, CSS link + "Powered by Azentis" footer + `id="page-login"` confirmed
- `curl -H "Host: dev.local" http://127.0.0.1:8000/assets/our_brand/css/our_brand.css` → 200, served byte-identical to source (no bundling/mangling of raw `public/css` files)
- Authenticated curl (`/api/method/login` + cookie jar) against `/app` → our_brand.css link present on desk shell too
- `python3 -c "from utils import contrast_text_color; print(contrast_text_color('#6D28D9','#06B6D4'))"` → `#FFFFFF`, matches DESIGN.md's stated platform-default `on-primary`
- `bench build --app our_brand` → succeeded, "Application Assets Linked"
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Architecture decision confirmed correct in practice**: the CSS-injection approach (not a `login.html` template replacement) worked cleanly — every AC was satisfiable by restyling the existing DOM via `#page-login`-scoped CSS, with only one small isolated template override needed (the footer include). No frappe/erpnext functionality (social login, LDAP, signup, forgot-password, email-link-login) was touched or put at risk.
- **Font vendoring turned out to be unnecessary**: Story assumed Inter would need self-hosting from scratch, but Frappe core already vendors it and already loads it on the login page via `login.bundle.css`. Verified this empirically before writing any font files, avoiding duplicate/wasted assets.
- **`update_website_context` hook name correction**: Dev Notes (written during story creation) guessed the hook might be called `website_context`; actual investigation of `frappe/website/page_renderers/base_template_page.py` showed the real hook is `update_website_context` (`frappe.get_hooks("update_website_context")`). Documented for accuracy, but ultimately not wired in this story (see Task 5's scope note) since there's no safe way to feed a computed value into `login.html`'s CSS without touching that template — the function exists and is correct, real per-render wiring is Story 1.7's job once Tenant Settings provides live colors and a template injection point is designed alongside it.
- **AC8 (`--login-background-image`) proven via live CSS reload, not a browser**: `public/css/*.css` in a Frappe app is served directly from the symlinked assets directory, unbundled — edits are visible via curl immediately with no `bench build` step. Used this to append a temporary override rule, confirmed via curl it was served, then removed it. This is a legitimate proof of the *mechanism* (the `var()` fallback swap is correct per CSS spec — a custom property set on `.page-content-wrapper` inherits to its own `::before` pseudo-element, and since `background-image`'s value is *only* the `var()` call, setting the property replaces the whole value, not just augments it) even without a browser to visually confirm.
- **No automated test framework** — consistent with Stories 1.1/1.2's documented, deliberate scope decision for this solo 1-month MVP. Verification here was curl/grep-based (HTTP status, exact HTML class/id presence, exact CSS selector/property signatures) plus direct specificity/cascade reasoning for the one real risk (load-order collision with `login.bundle.css`), not a browser rendering pass. Flagging this explicitly: dark-mode/reduced-motion/mobile-breakpoint *presence in the CSS* was verified; true pixel-level visual correctness in an actual browser was not.
- Frappe's `--primary` / `--brand-color` CSS custom property (used platform-wide by `.btn-primary`, links, etc. per `frappe/public/scss/common/css_variables.scss` and `buttons.scss`) was the existing, intended hook for AC1's "any page" requirement — overriding it at `:root` is a one-line, low-risk change that reuses Frappe's own theming mechanism rather than inventing a new one.

### File List

- `myerp/apps/our_brand/our_brand/hooks.py` (modified — `app_include_css`, `web_include_css`)
- `myerp/apps/our_brand/our_brand/utils.py` (new — `contrast_text_color()`)
- `myerp/apps/our_brand/our_brand/public/css/our_brand.css` (new)
- `myerp/apps/our_brand/our_brand/templates/includes/footer/footer_powered.html` (new)
