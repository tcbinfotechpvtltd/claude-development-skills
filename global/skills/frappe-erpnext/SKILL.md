---
name: frappe-erpnext
description: Builds and fixes Frappe and ERPNext apps on v15/v16 — doctypes, hooks, whitelisted APIs, reports, patches, print formats, workflows and bench. Use when working in a Frappe, ERPNext or HRMS app; when running bench; or when debugging a Frappe site.
---

# Frappe / ERPNext engineering

Security invariants for Frappe code are in the user rule `frappe-erpnext` (it auto-loads when app files are touched) and in [stacks.md](../eng-security/stacks.md). This skill holds the procedures.

## Core rules
- `apps/frappe` and `apps/erpnext` are never edited; customise through a custom app (fixtures, `hooks.py`, overrides).
- Commands touch only the site you were asked to work on; each client has an isolated site.
- A restored client site is neutralized before it first starts: emails muted, scheduler off, vendor credentials cleared.
- Whitelisted methods check permissions; user-facing reads use `frappe.get_list`, which applies them, and SQL is parameterized.
- Accounting and stock move only through documents, never direct GL or stock-ledger inserts, and queries on company-scoped doctypes filter by company.
- Patches are idempotent and listed in `patches.txt`; tests run on a dedicated test site.
- On a production bench: backup first, explicit approval, Server Scripts stay disabled.

## Before changing anything
- For a client ERPNext implementation, run the project with the ERP method in [erp-implementation.md](../eng-delivery/erp-implementation.md): configure standard features before writing any code.
- Identify bench path, Frappe/ERPNext versions (`bench version`), the site, its port, and which apps are installed (`bench --site <s> list-apps`). Record them in the project CLAUDE.md if they are missing.
- A restored copy of a client site is neutralized before its first start (mute emails, disable the scheduler, clear vendor credentials; [erp-implementation.md](../eng-delivery/erp-implementation.md)).
- Each client gets an isolated site (and usually its own port). Never run commands against a site you were not asked to touch. `bench serve` serves the default site for every host, so pin it with `bench --site <site> serve --port <port>`.
- Check whether the user wants changes **through the UI only** (some implementation projects forbid API/DB writes for business data). Infra and code changes go through bench and git.

## Where code goes
- Customize standard apps only through a custom app: Custom Fields / Property Setters exported as fixtures, `doc_events` and `override_doctype_class` in `hooks.py`, client scripts in the app's `public/js`. Never edit `apps/frappe` or `apps/erpnext` in place.
- DocType changes are made in developer mode (`bench --site <s> set-config developer_mode 1`) via the DocType UI or JSON, then committed with the app. Field renames and data moves need a patch.
- Patches: idempotent functions under `<app>/patches/`, listed in `patches.txt` (in the `[post_model_sync]` section when they depend on new schema). Re-running must be harmless.
- Controllers: validation in `validate`, side effects in `on_submit`/`on_cancel`; respect docstatus (0 draft, 1 submitted, 2 cancelled); never mutate submitted documents outside amend/cancel flows.
- Background work: `frappe.enqueue(..., queue="long", timeout=...)` with idempotent jobs; scheduler events in `hooks.py`.
- Reports: Query Reports with parameterized SQL and permission-aware filters; Script Reports for logic; always respect user permissions on company/branch.

## Accounting and stock (ERPNext)
- Post accounting and stock through documents (Journal Entry, Payment Entry, Stock Entry), never direct GL/SLE inserts. Cancellation creates reversing entries; keep it that way.
- Multi-company: every query filters by `company`; inter-company flows use Internal Customer/Supplier pairs.
- Use `flt()` and `cint()` with field precision (`frappe.get_precision`), `frappe.utils.getdate/add_days`, and company currency; avoid Python float arithmetic on totals without rounding to precision.

## Testing and verification
- `bench --site <test-site> run-tests --app <app> [--module ...]` on a dedicated test site, never on a client site. `FrappeTestCase` with fixtures created in `setUpClass`.
- After code changes: `bench --site <s> migrate` (applies patches and schema), `bench build --app <app>` for JS/CSS, `bench --site <s> clear-cache`, restart workers if jobs changed.
- Verify in the desk: open the form or report as a non-admin role to confirm permissions, not only as Administrator.

## Known gotchas
- **v16 setup-wizard reload loop** after forcing setup through the DB: set all of System Settings `setup_complete=1`, `is_setup_complete=1` on each Installed Application with a wizard, `frappe.db.set_default('setup_complete','1')`, and `frappe.db.set_default('desktop:home_page', '<workspace>')`, then `frappe.clear_cache()`.
- Realtime needs `node apps/frappe/socketio.js` (default 9001); with plain `bench serve` the socket 404s harmlessly.
- MariaDB from Homebrew: root uses unix_socket auth, so bench needs a separate password-auth admin user; record its name (never the password) in the project notes.
- New full-page forms in the desk may wipe the first fill after navigation when automated through the browser: re-check field values before saving.
- `frappe.get_all` ignores permissions; `frappe.get_list` applies them. Choose deliberately.
- Changing `encryption_key` or losing `site_config.json` breaks every Password field: back it up with the DB.

## Production safety
Production Frappe servers: backups first (`bench --site <s> backup --with-files`), migrations during a window, `bench restart` after deploys, and Server Scripts kept disabled. Any change on a production bench needs explicit user approval; the guard asks before bench-destructive commands and before mutating commands over SSH.
