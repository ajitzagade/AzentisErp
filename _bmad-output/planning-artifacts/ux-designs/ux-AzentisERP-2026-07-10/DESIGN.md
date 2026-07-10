---
name: 'AzentisERP Branding Layer'
description: 'White-label branding/theming layer for a multi-tenant ERP/CRM SaaS forked from ERPNext. This DESIGN.md covers ONLY the hero surfaces a tenant sees before/around the inherited ERPNext desk UI (login, splash) plus a restrained accent applied to the desk chrome. The inherited desk UI itself (lists, forms, reports) keeps its stock Frappe styling untouched except for that one accent.'
status: final
created: '2026-07-10'
updated: '2026-07-10'
colors:
  tenant-primary: '#6D28D9'
  tenant-secondary: '#06B6D4'
  on-primary:
    note: 'Computed server-side per render from the primary/secondary gradient''s relative luminance (white or near-black) — never hardcoded, so an arbitrary tenant color pair can never produce unreadable button text.'
  surface-mesh-base-light: '#F4F2FB'
  surface-glass-light: 'rgba(255,255,255,0.55)'
  surface-glass-light-fallback: 'rgba(255,255,255,0.92)'
  border-glass-light: 'rgba(255,255,255,0.65)'
  text-light: '#1B1725'
  text-muted-light: '#5B5468'
  surface-input-light: 'rgba(255,255,255,0.55)'
  border-input-light: 'rgba(27,23,37,0.14)'
  surface-mesh-base-dark: '#0E0B16'
  surface-glass-dark: 'rgba(24,20,34,0.55)'
  surface-glass-dark-fallback: 'rgba(24,20,34,0.92)'
  border-glass-dark: 'rgba(255,255,255,0.14)'
  text-dark: '#F3F1FA'
  text-muted-dark: '#B3ACC4'
  surface-input-dark: 'rgba(255,255,255,0.06)'
  border-input-dark: 'rgba(255,255,255,0.16)'
typography:
  display:
    fontFamily: 'Inter'
    fontSize: 18px
    fontWeight: '700'
    lineHeight: '1.25'
    letterSpacing: -0.01em
  body:
    fontFamily: 'Inter'
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'Inter'
    fontSize: 11px
    fontWeight: '600'
    letterSpacing: 0.01em
  caption:
    fontFamily: 'Inter'
    fontSize: 10.5px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 12px
  md: 16px
  lg: 22px
  full: 9999px
spacing:
  card-padding: '28px 26px 24px'
  card-padding-mobile: '24px 20px 20px'
  card-max-width-mobile: '340px'
  card-side-margin-mobile: '20px'
  touch-target-min: '44px'
  touch-target-primary: '48px'
  field-gap: '12px'
  section-gap: '16px'
  frame-radius: '{rounded.lg}'
components:
  login-card:
    background: '{colors.surface-glass-light}'
    background-dark: '{colors.surface-glass-dark}'
    background-fallback: '{colors.surface-glass-light-fallback}'
    background-fallback-dark: '{colors.surface-glass-dark-fallback}'
    border: '{colors.border-glass-light}'
    radius: '{rounded.lg}'
    backdropBlur: '18px'
    backdropSaturate: '150%'
  mesh-background:
    blob-1-color: '{colors.tenant-primary}'
    blob-2-color: '{colors.tenant-secondary}'
    blob-3-color: 'color-mix(50% blob-1, blob-2)'
    blur: '34px'
    animation: 'drift 14s ease-in-out infinite'
    animation-reduced-motion: 'none'
    override: 'Tenant Settings.login_background (image), when set, replaces this entire component — see Components section'
  button-primary:
    background: 'linear-gradient(120deg, {colors.tenant-primary}, {colors.tenant-secondary})'
    foreground: '{colors.on-primary}'
    radius: '{rounded.full}'
  input:
    background: '{colors.surface-input-light}'
    background-dark: '{colors.surface-input-dark}'
    border: '{colors.border-input-light}'
    radius: '{rounded.sm}'
  navbar-accent:
    background: '{colors.tenant-primary}'
    treatment: 'flat solid fill, no gradient, no blur, no animation'
---

# Design — AzentisERP Branding Layer

## Brand & Style

AzentisERP's own product premise is invisible: a tenant should never sense the ERPNext/Frappe foundation underneath. The brand expression carries that — an immersive, animated gradient-mesh backdrop built entirely from the tenant's own two brand colors, with a frosted glass card floating on top. It reads as premium, modern SaaS: the kind of first-screen a founder screenshots and puts on a landing page, not utilitarian back-office software.

That treatment is deliberately scoped to **hero surfaces only** — login and splash. The moment a user is inside the actual ERP (lists, forms, reports — all inherited stock ERPNext), the glass/mesh/motion disappears entirely. Working software needs legibility and speed, not ambient animation behind a data table. The only carry-through into the working UI is a single flat accent: the navbar tinted with the tenant's `primary_color`, plus their logo. Two registers, one rule: *hero surfaces sell the product, working surfaces get out of the way.*

This file specifies only that hero-surface brand layer and the one desk-chrome accent. It does not — and must not — restyle any inherited ERPNext component beyond that.

## Colors

Every visible color on a hero surface derives from exactly one of two sources: the **two tenant-controllable colors** (`{colors.tenant-primary}`, `{colors.tenant-secondary}` — sourced live from the Tenant Settings DocType, architecture AD-2/AD-3, never compiled into a static asset) or a small **fixed platform palette** for surfaces, text, and borders that is the same for every tenant and only varies by light/dark theme.

- **`{colors.tenant-primary}` / `{colors.tenant-secondary}`** — drive the animated mesh-gradient background and the primary button's gradient fill. Nothing else uses them directly. Platform default (pre-customization): `#6D28D9` violet / `#06B6D4` cyan.
- **`{colors.on-primary}`** — the button's text color. Never a fixed hex. Computed server-side from the gradient's relative luminance at render time (white on a dark gradient, near-black on a light one) so an arbitrary tenant color choice can never produce unreadable button text. This is the one color token in this system with no static value — see the `note` field in frontmatter.
- **Fixed light-theme surfaces** — `{colors.surface-mesh-base-light}` (#F4F2FB) behind the blobs, `{colors.surface-glass-light}` for the card (55% white, blurred), `{colors.text-light}` (#1B1725) / `{colors.text-muted-light}` (#5B5468) for all card copy. None of these ever change with tenant color — they're what keeps the card readable regardless of what mesh color sits behind it.
- **Fixed dark-theme surfaces** — mirror structure, `{colors.surface-mesh-base-dark}` (#0E0B16), `{colors.surface-glass-dark}`, `{colors.text-dark}` (#F3F1FA) / `{colors.text-muted-dark}` (#B3ACC4).
- **Desk-chrome accent** — `{colors.tenant-primary}` as a **flat, solid** navbar fill. No gradient, no glass, no blur here — this token is reused, not the glass/mesh treatment.

Avoid: any tenant color driving body text or input text color directly (always the fixed `text-light`/`text-dark` tokens); more than the two tenant colors anywhere; the mesh/glass treatment anywhere outside login and splash.

## Typography

**Inter**, self-hosted (no external font CDN — keeps every hero surface a self-contained asset, consistent with how the Branding App ships CSS via `app_include_css`). Four roles, all Inter:

- **`{typography.display}`** (18px/700) — the card's "Welcome back" headline and equivalent splash-screen wordmark treatment. The one place letter-spacing tightens (-0.01em) for a more designed feel.
- **`{typography.body}`** (13px/400) — input values, general card copy.
- **`{typography.label}`** (11px/600) — field labels ("Email address," "Password"), small caps-adjacent tracking.
- **`{typography.caption}`** (10.5px/400) — footnote/help text ("Trouble signing in?").

No serif, no display alternate — Inter's own weight range carries the full hierarchy. The inherited ERPNext desk UI keeps its own stock typography untouched; Inter is scoped to hero surfaces and the navbar wordmark only.

## Layout & Spacing

Single centered card (`{spacing.card-padding}`: 28px/26px/24px) floating over a full-bleed animated background — no grid, no multi-column hero layout. `{spacing.field-gap}` (12px) between form fields, `{spacing.section-gap}` (16px) between logical groups (header block → form → footnote).

The mesh background is full-viewport (`aspect-ratio` free, fills the surface) with three blurred color blobs positioned off-frame at the corners so no hard edge is visible.

**Below `md` (mobile — see `EXPERIENCE.md.Responsive & Platform` for the full behavioral rules):** the card switches to `{spacing.card-padding-mobile}` (24px/20px/20px), fluid width capped at `{spacing.card-max-width-mobile}` (340px) with a fixed `{spacing.card-side-margin-mobile}` (20px) margin — never the fixed desktop card width. Every input, the checkbox, and the forgot-password link meet `{spacing.touch-target-min}` (44px); the primary button meets `{spacing.touch-target-primary}` (48px). This is a deliberate viewport-scoped override, not a violation of the desktop spacing scale above.

## Elevation & Depth

Two elevation languages, deliberately different:

- **Glass card**: soft, diffuse shadow (`0 8px 32px rgba(0,0,0,0.14)`) plus the `backdropBlur`/`backdropSaturate` frost itself — depth comes from translucency, not a hard drop shadow.
- **Primary button**: a colored glow shadow tinted from `{colors.tenant-primary}` (`0 10px 28px color-mix(45% tenant-primary, transparent)`) — the one place elevation carries brand color, reinforcing it as the single call-to-action.

Desk-chrome navbar accent: flat, zero elevation — a solid color bar, not a floating/shadowed element.

## Shapes

- **`{rounded.lg}`** (22px) — the outer background frame and the glass card itself. The signature "soft, premium" radius.
- **`{rounded.md}`** (16px) — the logo mark only.
- **`{rounded.sm}`** (12px) — input fields.
- **`{rounded.full}`** (pill) — the primary button exclusively. No other element is pill-shaped.

## Components

- **Mesh background** (`{components.mesh-background}`) — three blurred (34px) blobs colored from `{colors.tenant-primary}`, `{colors.tenant-secondary}`, and a 50/50 mix of both, animated on a 14s ease-in-out drift loop. **Must** respect `prefers-reduced-motion: reduce` — animation disabled entirely, blobs render static, for any user who requests it. **Must** degrade gracefully when `backdrop-filter` is unsupported: the glass card falls back to `{colors.surface-glass-light-fallback}` / `{colors.surface-glass-dark-fallback}` (92% opaque, no blur) rather than rendering broken/transparent. **Default for the large majority of tenants** — every tenant gets this unless they've explicitly set an override (next).
- **Login background image override** — when a tenant sets `Tenant Settings.login_background`, that image renders full-bleed behind the glass card *instead of* the mesh background — the animated blobs are suppressed entirely, not layered under/over the image. The glass card, its blur/fallback behavior, and all typography/color tokens are unchanged either way; only the background layer differs. This is the exception, not the default — most tenants never set it and get the mesh.
- **Login card** (`{components.login-card}`) — the frosted glass container. Logo mark + tenant name at top, `{typography.display}` headline, `{typography.body}` sub-line, two `{components.input}` fields, remember-me + forgot-password row, `{components.button-primary}`, `{typography.caption}` footnote.
- **Splash screen** — same mesh background and glass language, reduced to a centered logo mark and a loading indicator; no form, no footnote.
- **Desk-chrome accent** (`{components.navbar-accent}`) — the *only* place this system touches post-login UI: a flat `{colors.tenant-primary}` navbar fill plus the tenant's logo. Everything else in the desk UI is untouched stock ERPNext/Frappe styling.
- **Transactional email header** — logo + a `{colors.tenant-primary}` accent bar in a plain HTML header block. No gradient, no glass, no animation — none of those render reliably across email clients, and the register is transactional, not a hero moment.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Keep the glass/mesh/motion treatment to login + splash only | Extend glass, blur, or the animated mesh into any post-login desk screen |
| Compute button text color from gradient luminance at render time | Hardcode white (or any fixed color) as button text |
| Render all card/body text in the fixed light/dark `text` tokens | Let a tenant color drive body or input text color |
| Respect `prefers-reduced-motion` — disable the mesh drift | Force the drift animation on users who've opted out of motion |
| Fall back to a near-opaque card when `backdrop-filter` is unsupported | Ship a broken transparent/unreadable card on unsupported browsers |
| Use exactly two tenant colors (`tenant-primary`, `tenant-secondary`) everywhere | Introduce a third brand color, or let tenants set more than two |
| Self-host Inter | Load fonts from an external CDN |
| Treat `login_background` as the rare exception (mesh is the default) | Encourage every tenant to upload a background image — the designed mesh is the intended experience |
| Wire `favicon` directly from Tenant Settings, no token needed | Add a `favicon` DESIGN.md token — it's a plain browser-tab icon, out of this system's scope |
| Fix input font-size at 16px on mobile viewports | Let mobile inputs inherit the 13px desktop `{typography.body}` size — triggers iOS Safari's auto-zoom-on-focus |
| Use `dvh` for full-bleed background height | Use bare `vh` — clips under mobile browser chrome or an open keyboard |
| Test the mobile card against `env(safe-area-inset-*)` devices | Assume every phone has a straight top/bottom edge — modern notches and home indicators will clip an unpadded card |
