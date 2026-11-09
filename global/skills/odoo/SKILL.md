---
name: odoo
description: Building, customising and upgrading Odoo modules (Community and Enterprise, versions 17 to 20): module layout and naming, ORM and view changes per version, access rights and record rules (ir.access in 20), controllers, QWeb reports, tests with odoo-bin, migration scripts and the upgrade service, performance. Use when working on any Odoo addon, database or implementation.
---

# Odoo engineering

## Core rules
- Write for the project's Odoo version: 17 to 20 break code differently (see the version table in this skill).
- Core addons are never edited; extend through a custom module with `_inherit`, xpath view inheritance and overrides that call `super()`.
- Every new model ships with access rights and record rules, multi-company rules included.
- Public methods are RPC endpoints, so they check access and validate input; `sudo()` needs a written reason.
- SQL goes through the ORM or the `SQL` wrapper with parameters, domains are never built by concatenating input, and code never calls `cr.commit()`.
- Every database copy is neutralized (`odoo-bin neutralize`) before it starts; module upgrades run on a copy first.
- Tests run on a test database, with key ones run as a non-admin user.

## Before changing anything
- Client implementations follow the phase-by-phase method in skill `eng-delivery` ([erp-implementation.md](../eng-delivery/erp-implementation.md)): standard first, configuration second, code only for real gaps.
- Confirm the Odoo version and edition (Community or Enterprise; on-premise, Odoo.sh or Online), the database, the addons path and the custom modules, and record them in the project CLAUDE.md. Code differs materially between 17, 18, 19 and 20 (table below): write for the project's version.
- Standard support (checked 2026-11-04) lasts 3 years: 20.0 (Sept 2026 to Sept 2029), 19.0 (to Sept 2028), 18.0 (to Sept 2027). **17.0 left standard support in Sept 2026**: flag it and plan the upgrade. The SaaS versions (x.1 to x.4) exist only on Odoo Online.
- Never edit core addons. Extend through a custom module: `_inherit`, view inheritance with `xpath`, and method overrides that call `super()`.
- Upgrading modules or migrating data happens on a copy of the database first. Production needs approval and a backup.
- **Neutralize every copy before its first start**: `odoo-bin neutralize -d <copy>`. Otherwise its mail servers, scheduled actions and payment, SMS or e-invoicing credentials stay live, and the first run can email customers or call providers. A copy still holds client personal data: keep it access-controlled and delete it when done.

## Module layout and naming (official coding guidelines)
- **Folders**: `models/`, `views/`, `security/`, `data/`, `controllers/`, `wizard/`, `report/`, `tests/`, `static/` (20.0 adds `populate/`). One model per file, named after the model.
- **Files**: `<model>_views.xml`, `<module>_menus.xml`, `<model>_templates.xml`, `<module>_groups.xml`, `<model>_security.xml`; a controller file is `<module_name>.py`.
- **XML ids**: `<model>_view_<type>`, `<model>_action`, `<model>_menu`, `<module>_group_<name>`. An inherited view keeps the original id with an `.inherit.<module>` suffix on its name. Write `id` before `model` on records.
- **Python**: imports grouped as standard library and external, then `odoo`, then `odoo.addons`, alphabetical within each group (`from odoo import Command, _, api, fields, models`).
  - Method prefixes `_compute_`, `_search_`, `_default_`, `_onchange_`, `_check_`; `action_` methods call `self.ensure_one()`; relational fields end in `_id` or `_ids`.
  - Never call `cr.commit()` or `rollback()` yourself, and catch specific exceptions only.
  - Translate with `self.env._('literal')` where the version provides it (it is what the current guidelines use), otherwise `_()`. Prefix custom context keys with the module name. Prefer `filtered`, `mapped` and `sorted` over manual loops.
- **Manifest**: a full version (for example `19.0.1.0.0`), minimal `depends`, data files in load order (security first), a licence.

## Version changes that break code (official ORM changelog)
| Since | Change |
|---|---|
| 17.0 | `attrs` and `states` removed from views: use Python-expression attributes such as `invisible="state != 'draft'"`. `name_get` deprecated: override `_compute_display_name`. New `search_fetch`/`fetch` and the `SQL` wrapper |
| 18.0 | `<tree>` views are `<list>`. `group_operator` is `aggregator`. `check_access_rights`/`check_access_rule` are replaced by `check_access`, `has_access` and `_filtered_access` |
| 19.0 | `read_group` deprecated: use `_read_group` in backend code, `formatted_read_group` for formatted results. `_sql_constraints` replaced by `models.Constraint`, `models.Index` and `models.UniqueIndex` class attributes. `Domain` builder. `@api.private`. JSON routes are `type='jsonrpc'`. `record._cr`, `_context` and `_uid` deprecated (use `env.cr`, `env.context`, `env.uid`). `odoo.osv` deprecated. `create` takes `vals_list` with `@api.model_create_multi` |
| 20.0 | `ir.access` (`security/ir.access.csv`: `id,name,model_id,group_id/id,operation,domain`) replaces model access lists and record rules. Binary fields use `BinaryValue`. `_table_query` removed. No `request` in model code. New HTTP server |

## Security
- **Every new model gets access rights and record rules.**
  - Up to 19: `ir.model.access.csv` with read/write/create/unlink per group, plus `ir.rule` records with `domain_force`.
  - 20: `ir.access` entries, with the operation subset and an optional domain.
  - Global rules intersect, group rules add up. Always include multi-company rules.
- **Groups**: access adds up across groups, so grant the least and use implied groups. Put `groups=` on sensitive fields (salary, bank, KYC): restricted fields disappear from views and raise on read or write.
- **Public methods are RPC endpoints.** Methods without a leading `_` take untrusted arguments, so check access and validate input. Make helpers private (`_name`, and `@api.private` on 19+).
- **`sudo()`** bypasses access checks and can cross company rules. Use it only for a written reason, after checking the caller's own rights, and never hand sudo'ed records back to the user. `with_user()` runs as a specific user.
- **Controllers**: `auth='user'` by default; `public` or `none` only with explicit validation; `bearer` for API keys where available (present in 19; 20 requires `bearer_scope`). CSRF is on for `type='http'` and off for JSON-RPC, so JSON routes rely on authentication checks. Always set explicit `methods=[...]`, and `cors` only for named origins.
- **SQL and domains**: the ORM or the `SQL` wrapper with parameters, never string formatting. Build domains with `Domain`, not by concatenating lists from input.
- **QWeb**: `t-out` escapes. Never wrap user-supplied content in `Markup`.

## QWeb reports
An `ir.actions.report` plus a QWeb template, with the paper format set explicitly. The PDF engine and fonts on the server decide the output, so check layout on the same server build as production. Keep report logic in a model method, not in the template.

## Testing
- Files `tests/test_*.py`, imported in `tests/__init__.py`.
  - `TransactionCase` rolls back after each test.
  - `HttpCase` adds `start_tour` and `browser_js`.
  - `Form` simulates the UI, onchanges included.
  - Choose `at_install` or `post_install` explicitly with `@tagged`.
- Run one module on a test database, never a client one: `odoo-bin -d <test_db> -u <module> --test-tags /<module> --stop-after-init` (use `-i` for a first install).
- Prove record rules by running key tests as a non-admin user (`with_user`).

## Upgrades and data migration
- **Upgrade scripts**: any change that needs one bumps the module version in `__manifest__.py`. Scripts live in `<module>/migrations/<full-version>/` as `pre-*.py`, `post-*.py` or `end-*.py`, each defining `migrate(cr, version)`.
  - `pre` runs before the module loads, `post` after it and its dependencies update, `end` after all modules.
  - Within each phase, files run in lexical order. Scripts must be idempotent.
- **CLI**: `-u <module>` updates (on a copy first), `-i` installs. `--reinit` reloads data in install mode: it overwrites `noupdate` records (customised templates, rules), also reinitialises dependent modules and still runs `post` scripts. Use it only on throwaway copies.
- **Renames and moves**: `odoo/upgrade-util` (`from odoo.upgrade import util`).
- **Major upgrades**:
  - The official upgrade service returns an upgraded test database, but custom modules must be ported to the target version first. Community projects often use OCA OpenUpgrade.
  - Plan in this order: port modules → test upgrade → UAT → timed rehearsal → production window with backup and rollback.

## Performance
- No ORM calls inside loops:
  - `create(vals_list)` once;
  - one `_read_group` instead of a `search_count` per record;
  - `search_fetch(domain, fields)` to search and load together;
  - keep prefetching (`with_prefetch`) when iterating.
- **Indexes**: `index=True` (or `'btree_not_null'`, or `'trigram'` for text search) on fields used in frequent domains. Indexes slow writes.
- **Stored computed fields** need precise `@api.depends`.
- **Measure** with the built-in profiler before optimising.

## Production basics
Run behind nginx with `proxy_mode` on, `list_db = False`, a strong master password, a `dbfilter`, workers and time limits sized for the server, and backups with restore tests (skill `eng-ship`).

Sources (checked 2026-11-04): odoo.com/documentation 19.0 and 20.0 (supported versions, coding guidelines, ORM changelog, security, HTTP routes, testing, CLI, upgrade scripts, upgrade service, performance); github.com/odoo/odoo source (20.0, 19.0); github.com/odoo/upgrade-util.
