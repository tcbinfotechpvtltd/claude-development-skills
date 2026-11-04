---
paths:
  - "**/application/controllers/**"
  - "**/application/models/**"
  - "**/application/libraries/**"
  - "**/application/views/**"
  - "**/application/config/**"
---
# eng-os rule: PHP CodeIgniter 3 code
Applies because CodeIgniter 3 application code is being touched. Procedures: skill `custom-apps` ([php-ci3.md](../skills/custom-apps/php-ci3.md)); security checklist: [stacks.md](../skills/eng-security/stacks.md).
- Queries use Query Builder or bindings; request input is never interpolated into SQL.
- Views escape output (`html_escape()`); CSRF protection stays on, with signature-verified webhooks as the only exclusions.
- Keys and credentials stay out of committed config files.
- Only new and changed code is restyled; whole-file reformatting buries the real change.
