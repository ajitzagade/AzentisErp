---
name: 'AzentisERP Branding Layer'
status: final
created: '2026-07-10'
updated: '2026-07-10'
sources:
  - '_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/prd.md'
  - '_bmad-output/planning-artifacts/prds/prd-AzentisERP-2026-07-10/addendum.md'
  - '_bmad-output/planning-artifacts/architecture/architecture-AzentisERP-2026-07-10/ARCHITECTURE-SPINE.md'
  - '_bmad-output/planning-artifacts/epics.md'
---

# AzentisERP Branding Layer — Experience Spine

> Scope note: this spine covers ONLY the white-label branding/theming surfaces (login, splash, transactional email, one desk-chrome accent). The inherited ERPNext desk UI itself — every CRM/Sales/Accounting/HR/Inventory/Projects screen — is untouched stock Frappe behavior and out of scope here entirely.

## Foundation

Responsive web. The hero surfaces (login, splash) are custom-built — they sit *in front of* Frappe's own desk UI, which has its own legacy styling system (not shadcn/MUI/a modern component library) that this spine does not touch beyond the one navbar accent. `DESIGN.md` is the visual identity reference for colors, type, and component tokens; this file owns behavior, states, and flows.

Single-tenant experience per site — each Frappe site is one tenant (architecture AD-2/AD-4), so there is never a tenant-switcher or multi-tenant UI inside a single session. A user logging into `priyastore.our-platform.com` sees only Priya's General Store's branding and modules; the platform-default look in `DESIGN.md` only appears for the platform operator's own unbranded site, or for a brand-new tenant before its Tenant Settings record is filled in.

## Information Architecture

| Surface | Reached from | Purpose |
|---|---|---|
| Login | Direct URL, or link in a welcome/notification email | Authenticate into the tenant's own branded instance |
| Splash / loading transition | Immediately after successful login, before the desk UI is ready | Bridges the branded hero moment into the inherited desk UI without a flash of unstyled/default content |
| Desk UI (inherited, out of scope) | Post-login | The actual ERP. Stock ERPNext, every screen. Only the navbar carries `{colors.tenant-primary}` as a flat accent — see `DESIGN.md.components.navbar-accent`. |
| Transactional email | System-triggered (welcome, password reset, notification) | Branded touchpoint that exists entirely outside the app session |

→ Composition reference: `mockups/login-full-bleed-glass.html` (desktop), `mockups/login-mobile.html` (real 390px phone viewport), `mockups/splash-loading.html`, `mockups/navbar-accent.html`. Transactional email header has no separate mockup — `DESIGN.md.Components` prose is sufficient (plain logo + accent bar, no layout complexity). Spine wins on conflict.

## Voice and Tone

Microcopy for login, splash, and transactional email. Brand aesthetic lives in `DESIGN.md`; this is language only. Audience: SMB business owners and staff in India, many using ERP software or this specific product for the first time — trustworthy and professional, not playful, not cold/generic-enterprise either.

| Do | Don't |
|---|---|
| "Welcome back" / "Sign in to continue to your workspace" | "Let's get started! 🎉" |
| "Trouble signing in? Contact admin" | "Oops! Something went wrong." |
| "Setting up your workspace…" (splash) | "Please wait" / a bare spinner with no label |
| Plain, declarative error text: "That password didn't match." | Jokey or falsely casual error copy |
| Same tone regardless of tenant — the *words* never change per tenant, only the colors/logo do | Tenant-specific copy variants (out of scope; Tenant Settings controls visuals, not microcopy) |

## Component Patterns

Behavioral. Visual specs live in `DESIGN.md.Components`.

| Component | Use | Behavioral rules |
|---|---|---|
| Login card | Login surface | Renders once Tenant Settings resolves (via the AD-2 cached accessor). Email + password fields, remember-me checkbox, forgot-password link, single primary submit button. Enter key in either field submits the form. |
| Mesh background | Login, splash | Purely decorative — see Accessibility Floor for `aria-hidden`. Colors derive live from `{colors.tenant-primary}`/`{colors.tenant-secondary}`; drift animation per `DESIGN.md.components.mesh-background`. |
| Splash / loading | Between login success and desk UI ready | Same mesh background, centered logo mark, a loading indicator. No interactive elements. Auto-dismisses when the desk UI finishes loading — never requires user action, and times out to a plain error state if desk-load fails (see State Patterns). |
| Navbar accent | Every inherited desk screen | The only branding surface inside the working app. Flat `{colors.tenant-primary}` fill + tenant logo. No hover/interaction change from stock Frappe navbar behavior — purely a color/logo swap. |
| Transactional email header | Welcome, password reset, notification emails | Logo + `{colors.tenant-primary}` accent bar, plain HTML, no animation/gradient/blur (email-client constraint, `DESIGN.md`). |

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| Tenant Settings not yet configured (new tenant, empty record) | Login, splash, navbar | Fail open to the platform-default `DESIGN.md` colors/logo (architecture spine's fail-open convention) — never a broken/blank branding surface. |
| Tenant has set `login_background` | Login, splash | Uploaded image renders full-bleed in place of the animated mesh; glass card and all other tokens unchanged. The exception path — most tenants never set this and get the mesh by default. |
| Malformed Tenant Settings record | Login, splash, navbar | Same fail-open behavior as above; logged server-side, never surfaced as a user-facing error on the login screen itself. |
| Wrong credentials | Login | Inline error text below the password field: "That password didn't match." Fields retain entered email (not password). No lockout messaging at MVP — that's inherited Frappe auth behavior, unchanged. |
| `prefers-reduced-motion: reduce` | Login, splash | Mesh blobs render static (no drift animation) — see Accessibility Floor. |
| `backdrop-filter` unsupported | Login, splash | Glass card renders at the fallback near-opaque background (`DESIGN.md` fallback tokens) — no blur, but never transparent-and-unreadable. |
| Desk UI fails to load after splash | Splash → transition | Splash does not spin forever — after a bounded timeout, replaces the loading indicator with a plain "Something went wrong loading your workspace. Retry" state (still on the mesh background, no glass card needed for a single message + button). |
| Session expired mid-session | Any inherited desk screen | Standard Frappe re-auth redirect to the branded Login surface — not a special AzentisERP-specific interstitial. |

## Interaction Primitives

Login is deliberately simple — no keyboard-shortcut surface, no command palette (that's a desk-UI-inherited concern, out of scope).

- `Enter` in email or password field submits the login form.
- `Tab` order: email → password → remember-me checkbox → forgot-password link → submit button — matches visual top-to-bottom order.
- Mouse/touch: standard click/tap on all interactive elements; no drag, no hover-only affordance (the card has no hover-revealed content — everything is visible by default, since this is a first-touch surface for often first-time software users).
- Splash surface has zero interactive elements during normal operation — only the timeout-error state introduces a button.

## Accessibility Floor

Behavioral rules; visual contrast mechanics live in `DESIGN.md`.

- WCAG 2.2 AA target across login, splash, and the navbar accent.
- **Motion**: `prefers-reduced-motion: reduce` disables the mesh drift animation entirely (not just slows it) — this is a hard requirement, not a nice-to-have, since the animation is decorative and has zero functional purpose.
- **Decorative background**: the mesh background and blobs are `aria-hidden="true"` — a screen reader should never announce "image" or describe the animated gradient; it's pure visual atmosphere, not content.
- **Focus visibility on glass**: the frosted/translucent card surface can weaken a default focus ring's contrast. Rule: focus rings on inputs and the submit button use a fixed (non-tenant-color-dependent) high-contrast outline — never rely on the tenant's primary/secondary color alone for focus visibility, since an arbitrary tenant color could produce a low-contrast ring against the glass surface.
- **Button text contrast**: enforced by `DESIGN.md`'s server-computed `{colors.on-primary}` — no arbitrary tenant color pair can ship unreadable button text.
- **Labels**: every input has a visible, associated `<label>` (not placeholder-as-label) — placeholders in the mockup ("you@company.com") are examples inside the field, not a replacement for the label above it.
- Screen reader announces the surface on load: "Sign in to {tenant_name}" as the page's accessible name, so a screen-reader user immediately knows which tenant's instance they're authenticating into.

## Responsive & Platform

Mobile is not an edge case here — Flow 1 below has Priya logging in from her phone, and that's the realistic default for a first-time SMB user, not the exception. Validated against a real 390px-wide (iPhone-class) render, not a scaled-down desktop screenshot — see `mockups/login-mobile.html`.

| Breakpoint | Behavior |
|---|---|
| `≥ md` (768px+) | Centered glass card over the full-bleed mesh background, fixed max-width, as in the desktop mockups. |
| `< md` (mobile) | Card is fluid width: `100%` minus a fixed side margin, capped at a max-width (`{spacing.card-max-width-mobile}` in `DESIGN.md`) — never a fixed desktop-px card squeezed onto a phone. Mesh blobs scale down proportionally (~35% smaller) — same color/animation logic, just sized for the smaller canvas. |

**Concrete mobile rules (apply on all viewports `< md`, not just "make it smaller"):**

- **Input font-size is fixed at 16px minimum**, regardless of the `{typography.body}` token's 13px desktop value. Below 16px, iOS Safari auto-zooms the viewport on input focus — a real, well-known mobile bug, not a style preference. This is a deliberate per-viewport override, not an inconsistency with `DESIGN.md`.
- **Touch targets are minimum 44×44px** on every input, the remember-me checkbox, and the forgot-password link (Apple HIG / WCAG 2.5.5); the primary submit button is 48px tall — a comfortable one-thumb tap target, not just "big enough."
- **Viewport height uses `dvh` (dynamic viewport height), never bare `vh`**, on the full-bleed background — mobile browser chrome (address bar collapse/expand) and an open on-screen keyboard must never clip the card or the mesh background.
- **`env(safe-area-inset-*)` padding** on the outer frame — clears the notch and home-indicator on modern iPhones; the card must never render underneath either.
- Splash and login share every rule above identically — the splash transition is just as likely to be seen on a phone as the login card is.

The inherited desk UI's own responsive behavior (out of scope here) is whatever stock Frappe/ERPNext already does — this spine only governs the hero surfaces and the navbar accent, per its stated scope.

## Key Flows

### Flow 1 — UJ-2: Priya's first login (mirrors PRD UJ-2)

1. Priya, who owns a small retail shop in Pune and has never used ERPNext or heard of Frappe, receives a welcome email from Ajit's onboarding pipeline (Epic 4). The email header carries her shop's logo and `{colors.tenant-primary}` accent — no Frappe/ERPNext branding anywhere in it.
2. She taps the login link on her phone.
3. The login surface renders: full-bleed animated mesh in her shop's two brand colors, frosted glass card, her logo and "Priya's General Store" at the top. Nothing here reads as generic or unfamiliar software.
4. She enters her email and password (provided in the welcome email) and hits Enter.
5. **Climax:** a brief splash transition — same mesh language, her logo, a loading indicator — bridges into the desk UI. When it resolves, she sees a navbar tinted with her own brand color and a sidebar showing only Stock, POS, Accounts, and CRM (her Retail preset, Epic 3) — no unfamiliar modules, no trace of Frappe or ERPNext anywhere she's looked so far.
6. **Resolution:** she starts entering her first product without asking anyone for help — realizes PRD UJ-2's climax exactly ("it feels like software made for her business").

Failure: wrong password on first try → inline error below the password field, email retained, she re-enters the password from the welcome email and succeeds on the second attempt. No lockout, no jarring error page.

### Flow 2 — Accessibility: a reduced-motion, dark-mode user logs in

1. A tenant's staff member has both dark mode and reduced-motion preferences set at the OS level (common combination — motion sensitivity and light sensitivity often co-occur).
2. They open the login link. The page respects `prefers-color-scheme: dark` automatically — dark mesh base, dark glass surface, light text — without a manual toggle needed.
3. **Climax:** the mesh blobs render in their tenant's brand colors but *static* — no drift animation — because `prefers-reduced-motion: reduce` is honored unconditionally. The visual identity (colors, glass, logo) is fully intact; only the motion is removed.
4. They tab through email → password → submit using keyboard alone; the focus ring is clearly visible against the dark glass surface (fixed high-contrast outline, not tenant-color-dependent).
5. **Resolution:** full brand experience, zero motion, full keyboard operability — no degraded "accessibility mode" that looks or feels like a lesser version of the product.
