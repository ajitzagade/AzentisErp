---
baseline_commit: ece3a97
---

# Story 1.5: Branded Transactional Email

Status: done

## Story

As a tenant's staff user,
I want welcome/notification/password-reset emails to carry our brand name and footer,
so that emails don't look like they came from a stranger's product.

## Acceptance Criteria

1. Given a password-reset email is triggered, when it sends, then the sender name and footer text are ours, not Frappe/ERPNext defaults.
2. Given a welcome or generic notification email is triggered, when it sends, then the same brand override applies, and GPLv3 license notices in any underlying template source remain untouched (NFR7) — only visible brand text changes.

## Dev Notes — Read Before Starting

**Two independent mechanisms, investigated during story creation — do not conflate them:**

**(a) Footer text** — `frappe/email/email_body.py::get_footer()` renders `templates/emails/email_footer.html` with a `default_mail_footer` arg sourced from `frappe.get_hooks("default_mail_footer")`. This hook is **collected across all installed apps as a list**, not "last app wins" — ERPNext's `hooks.py` already defines `default_mail_footer = """<span>Sent via <a href="...">ERPNext</a></span>"""` (`erpnext/hooks.py:482`), and if `our_brand` also defined this hook, both would render together (additive, not override). **Do not** add a `default_mail_footer` hook to `our_brand/hooks.py` expecting it to replace ERPNext's — it won't. Instead, override `templates/emails/email_footer.html` itself in `our_brand` (same reverse-install-order Jinja `ChoiceLoader` mechanism already proven for `footer_powered.html` in Story 1.3 and `splash_screen.html` in Story 1.4) and simply don't render the `default_mail_footer` variable at all — write our own footer text directly.

**(b) Sender name** — for system-triggered emails (password reset, welcome), `frappe/core/doctype/user/user.py::send_login_mail()` passes `sender=None` when triggered by Administrator/Guest (the common case for these flows), which falls through to `frappe.email.doctype.email_account.email_account.EmailAccount.default_sender` — `email.utils.formataddr((self.name, self.get("email_id")))`, i.e. **the Email Account record's own docname becomes the visible sender display name**. Investigated the fallback chain when no real Email Account is configured (confirmed empirically: this dev site has zero `Email Account` records, `mail_server`/`auto_email_id` unset in site config): `EmailAccount.find_default_outgoing()` → `find_from_config()` (nothing in site config) → `create_dummy()`, which is **hardcoded in Frappe core** to `{"name": "Notifications", "email_id": "notifications@example.com"}` (`email_account.py:379-380`) — not overridable via hooks, and not something we can touch (AD-1). The only real fix is to make a genuine `Email Account` record exist and be the default outgoing one, named for our brand, so `find_one_by_filters(enable_outgoing=1, default_outgoing=1)` finds it *before* ever reaching the hardcoded dummy fallback.
- Create this in `install.py::after_install()`: an `Email Account` doc named `"Azentis"`, `enable_outgoing=1`, `default_outgoing=1`, **`awaiting_password=1`** (this flag independently short-circuits `EmailAccount.validate()`'s live-SMTP-connection-test block regardless of `frappe.local.flags.in_install`, confirmed by reading `validate()` — safe to create without real SMTP credentials, which this platform-branding story has no business owning; real SMTP provisioning is an infrastructure concern for a later epic). Also set `always_use_account_name_as_sender_name=1` — a real Frappe flag (`email_body.py::replace_sender_name()`) that forces the Email Account's own name to be used as the sender display name even when a session-user-based sender was otherwise computed, which is exactly the "make it always ours" behavior AC1 wants.
- Mirror in `before_uninstall()`: delete the "Azentis" Email Account so uninstall cleanly returns to stock behavior (same isolation discipline as Story 1.2/1.4's `before_uninstall`).
- **This does not make real email delivery work in this dev sandbox** (no SMTP server configured, unchanged by this story) — that's out of scope. What's verifiable and is this story's actual deliverable: the *sender identity that would be used* is correctly "Azentis," confirmed via `frappe.sendmail()` + inspecting the resulting `Email Queue` record's `sender` field (which is written regardless of whether the later SMTP transmission step succeeds).

**NFR7 (GPLv3 notices untouched)** — checked: no GPLv3/license text is rendered inside any email template's visible output (`app_license` is `hooks.py` metadata, unrelated to email content, and this story never touches `hooks.py`'s license fields or any LICENSE file). This AC clause is satisfied by scope discipline, not by any specific new code — confirm and note this in Completion Notes rather than treating it as a task needing its own artifact.

**Both mechanisms are genuinely independent** — footer is a template override (like Stories 1.3/1.4), sender identity is a data record (like Story 1.2's `Website Settings` approach). Don't try to solve both through one mechanism.

### Previous Story Intelligence (1.1–1.4)

- `after_install()`/`before_uninstall()` in `our_brand/our_brand/install.py` already exist and follow a clear set/clear symmetry pattern (Website Settings `app_name`/`app_logo`/`splash_image`) — extend the same file, same pattern, for the new Email Account record.
- Template overrides go in `our_brand/our_brand/templates/...` at the exact same relative path as the frappe/erpnext file being overridden; reverse-install-order `ChoiceLoader` in `frappe/utils/jinja.py::get_jloader()` makes `our_brand`'s copy win automatically (proven twice already, Stories 1.3 and 1.4).
- Verification method: `bench --site dev.local console` (or a scratch script piped into it) for anything requiring real Python/ORM interaction (Email Account creation, `frappe.sendmail()` + Email Queue inspection) — curl alone can't verify email content since there's no public HTTP surface for outbound mail.
- Gotcha carried forward: don't manually start Redis on ports 11000/13000 outside `bench start`'s own Procfile; `bench build --app our_brand` needed after adding new files that aren't raw `public/css`.

## Tasks / Subtasks

- [x] Task 1: Override the email footer template (AC: 1, 2)
  - [x] Created `our_brand/our_brand/templates/emails/email_footer.html` — kept `email_account_footer`/`sender_address`/`email-pixel` blocks intact, replaced the `default_mail_footer` block with a static "Sent via Azentis" line, no reference to the hook variable
- [x] Task 2: Create a branded default outgoing Email Account (AC: 1, 2)
  - [x] Extended `install.py::after_install()` with `create_default_email_account()`: `Email Account` "Azentis" (`email_account_name` — confirmed via the doctype JSON's `autoname: field:email_account_name`, not a guessed fieldname), `enable_outgoing=1`, `default_outgoing=1`, `awaiting_password=1`, `always_use_account_name_as_sender_name=1`, `email_id="no-reply@azentis.local"`; idempotent via `frappe.db.exists` guard
  - [x] Extended `before_uninstall()`: deletes the "Azentis" Email Account symmetrically
- [x] Task 3: Build and verify (AC: all)
  - [x] `bench build --app our_brand` — succeeded
  - [x] Re-ran `after_install()` on the existing `dev.local` site — Email Account created without error (confirms `awaiting_password=1` correctly bypassed the live-SMTP-connection-test validation block, no real SMTP needed)
  - [x] Verified via `bench --site dev.local console`: Email Account "Azentis" exists with all four flags set as `1`; `frappe.sendmail(...)` → resulting `Email Queue` record's `sender` = `"Azentis <no-reply@azentis.local>"`, `message` contains `"Sent via Azentis"`, and does **not** contain "ERPNext" — all three assertions passed
  - [x] `myerp/apps/frappe` and `myerp/apps/erpnext` confirmed git-clean, unchanged from Story 1.1 baseline

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (claude-sonnet-5)

### Debug Log References

- `bench build --app our_brand` → succeeded
- `bench --site dev.local execute our_brand.install.after_install` → succeeded, no output (Email Account created without SMTP validation error)
- `bench --site dev.local console` script: `EMAIL_ACCOUNT: Azentis 1 1 1 1` (name, enable_outgoing, default_outgoing, awaiting_password, always_use_account_name_as_sender_name); `SENDER: Azentis <no-reply@azentis.local>`; `FOOTER_PRESENT: True`; `ERPNEXT_TEXT_ABSENT: True`
- `git status --short` in `myerp/apps/frappe` and `myerp/apps/erpnext` → both clean

### Completion Notes List

- **Two genuinely independent mechanisms, as anticipated in Dev Notes**: the footer is a stateless template override (identical pattern to Stories 1.3/1.4's reverse-install-order Jinja wins), while the sender identity is a real data record, not a hook or template — `frappe.get_hooks("default_mail_footer")` collects *across* all installed apps rather than letting the last-installed app override, which would have silently produced "Sent via ERPNext" and "Sent via Azentis" both rendering together had a hooks-based approach been used instead of a template override. This was caught during investigation, before writing any code, by reading `get_footer()`'s actual aggregation behavior rather than assuming hook semantics.
- **`awaiting_password=1` as the key that makes Email Account creation safe without real SMTP**: confirmed by reading `EmailAccount.validate()` — this flag independently short-circuits the live-connection-test block regardless of the `in_install` flag's state, which matters because this story's retroactive re-run (via `bench execute`, not the real install flow) does not have `frappe.local.flags.in_install` set. Verified empirically too: the retroactive run succeeded with zero errors.
- **NFR7 (GPLv3 notices)** confirmed satisfied by scope discipline: grepped both `frappe`/`erpnext` email templates for any GPL/license text in rendered output (none exists — `app_license` is `hooks.py` metadata, unrelated to email content) and confirmed this story never touches `hooks.py`'s license fields or any LICENSE file in either read-only app.
- **Verification chose `frappe.sendmail()` + Email Queue inspection over the real password-reset flow** — this dev sandbox has no working SMTP (unchanged by this story, out of scope), so actual delivery isn't testable regardless of branding; inspecting the `Email Queue` record's `sender`/`message` fields tests exactly the mechanism this story changes (sender resolution, footer rendering) without needing a live mail server, and is the same code path `send_login_mail()` (password reset) ultimately calls into.
- No automated test framework, consistent with Stories 1.1–1.4's documented decision.

### File List

- `myerp/apps/our_brand/our_brand/install.py` (modified — `create_default_email_account()`, wired into `after_install`/`before_uninstall`)
- `myerp/apps/our_brand/our_brand/templates/emails/email_footer.html` (new)
