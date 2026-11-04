---
paths:
  - "**/__manifest__.py"
  - "**/security/ir.model.access.csv"
  - "**/security/ir.access.csv"
  - "**/views/*.xml"
  - "**/report/*.xml"
---
# eng-os rule: Odoo module code
Applies because an Odoo module file is being touched. Version-specific procedures: skill `odoo` (load it if it is not loaded yet; APIs differ between 17, 18, 19 and 20).
- Core addons are never edited; changes live in a custom module through `_inherit`, view `xpath` and overrides that call `super()`.
- Every new model ships with access rights and record rules (multi-company included); `sudo()` only with a written reason after checking the caller's rights.
- SQL only through the ORM or the `SQL` wrapper with parameters; domains built with `Domain`, never from concatenated input.
- A schema or data change bumps the manifest version and adds an idempotent script under `migrations/<version>/`.
- Copies of client databases are neutralized (`odoo-bin neutralize`) before they are started.
