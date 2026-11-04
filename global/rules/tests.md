---
paths:
  - "**/tests/**"
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*_test.dart"
  - "**/test/**/*.dart"
---
# eng-os rule: test code
Applies because test code is being touched. Strategy, test types and tooling: skill `eng-testing`.
- Tests are never deleted, skipped or weakened to make a run pass; a failing test is a finding.
- Each test checks one behaviour and is deterministic: frozen time, fixed seeds, no live vendors.
- Test data is synthetic, never real customer data.
- A bug fix comes with a test that failed before the fix.
