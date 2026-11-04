---
paths:
  - "docs/**"
  - "**/CHANGELOG.md"
---
# eng-os rule: project documents
Applies because project documentation is being touched. The document set and when each is updated: skill `eng-docs`.
- No secrets, credentials or real customer data in documents or screenshots.
- Requirement ids (`REQ-nnn`) stay stable; changes get a change-history row rather than silent edits.
- Progress-log entries are new files in `docs/progress/`; past entries are not rewritten.
- Business facts (rules, rates, dates) are marked **TO CONFIRM** until the client confirms them.
