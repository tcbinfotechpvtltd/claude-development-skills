---
paths:
  - "**/migrations/**"
  - "**/migrate/**"
  - "**/alembic/**"
  - "**/*.sql"
  - "**/schema.prisma"
  - "**/database/**"
---
# eng-os rule: database migrations and SQL
Applies because a migration or SQL file is being touched. Procedures: skill `eng-ship`.
- Every migration is reversible (down/rollback path or documented restore) and idempotent (safe to re-run).
- Expand then contract: add new columns/tables first, backfill, switch reads, remove old structures in a later release. Never rename or drop in the same deploy that changes code.
- Destructive DDL or bulk UPDATE/DELETE on shared or production data needs explicit user approval, a fresh verified backup, and a dry run on a production-like copy.
- Large backfills run in batches with progress logging; avoid long table locks on hot tables (online DDL where the engine supports it).
- Keep money as DECIMAL (never FLOAT/DOUBLE), timestamps in UTC, and add indexes for every new foreign key and frequent filter.
