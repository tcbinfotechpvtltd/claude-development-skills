---
paths:
  - "**/hooks.py"
  - "**/doctype/**"
  - "**/patches.txt"
  - "**/patches/**"
---
# eng-os rule: Frappe / ERPNext code
Applies because a Frappe app file is being touched. Full procedures: skill `frappe-erpnext`.
- `@frappe.whitelist()` methods check permission explicitly (`frappe.has_permission`, `doc.check_permission`, `frappe.only_for`) before reading or writing; `allow_guest=True` only for truly public endpoints, with input validation and rate limiting.
- No `ignore_permissions=True` / `ignore_user_permissions` unless the reason is documented in a comment and the caller is already authorized.
- `frappe.db.sql` only with `%(name)s` / `%s` parameters, never f-strings or concatenation; prefer `frappe.qb`, or `frappe.get_list` (permission-aware) when results reach a user.
- Server Scripts stay disabled (`server_script_enabled` off); business logic lives in the app's Python, under version control.
- Schema changes go through DocType JSON exported by the framework plus idempotent patches registered in `patches.txt`; never ALTER tables by hand.
- Money fields: `flt(value, precision)` with the field's precision; round once at the defined business rule; reconcile totals in tests.
