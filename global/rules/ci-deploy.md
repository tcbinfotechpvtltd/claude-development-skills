---
paths:
  - ".github/workflows/**"
  - "**/.gitlab-ci.yml"
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/compose*.yml"
  - "**/*.tf"
  - "**/deploy/**"
  - "**/nginx/**"
  - "**/k8s/**"
  - "**/Procfile"
  - "**/ecosystem.config.*"
---
# eng-os rule: CI/CD, containers and infrastructure
Applies because pipeline, container or infra config is being touched. Procedures: skill `eng-ship` and its [github.md](../skills/eng-ship/github.md) (load it if it is not loaded yet).
- CI tokens get least privilege (`permissions:` block, read-only by default); third-party actions pinned to a commit SHA; secrets only from the CI secret store, never echoed.
- Deploy jobs to production require a protected environment with manual approval; the same built artifact is promoted from UAT to production.
- Containers run as non-root with pinned base images, health checks and no secrets baked into layers.
- Infra changes are reviewed as a plan/diff before apply, and every deploy path has a written rollback.
- Public exposure is opt-in: databases, Redis, admin panels and debug ports never bind to public interfaces.
