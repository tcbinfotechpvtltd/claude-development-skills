# GitHub repository and Actions security

Changing repository settings, rulesets or secrets is a security-boundary change: Claude proposes the exact settings or `gh api` calls and the user applies or approves them.

## Repository baseline (repos we own)
- **Protect the default and release branches** with a ruleset (or classic branch protection):
  - require a pull request with at least one approval;
  - require code-owner review for sensitive paths;
  - dismiss stale approvals when new commits arrive;
  - require the CI status checks to pass;
  - block force pushes and deletion.
  - Optional: linear history, signed commits.
  - Keep the bypass list empty or minimal. Rulesets stack (the most restrictive rule wins) and can also protect tags.
- **CODEOWNERS** in `.github/CODEOWNERS` (the root or `docs/` also work; the first found wins). Owners need write access, and the last matching pattern wins. Always own `.github/workflows/` and deploy or infra files.
- **Dependabot**: turn on alerts and security updates. Add `.github/dependabot.yml` (`version: 2`, one `updates:` entry per ecosystem, including `github-actions`).
- **Secret scanning and push protection**: free and on by default for public repos. Private repos need GitHub Secret Protection, a paid add-on for Team or Enterprise plans. Without it, run gitleaks in pre-commit and CI.
- **Templates**: PR template, `release.yml` and CHANGELOG from `~/.claude/eng-os/templates/release/` (see [releases.md](releases.md)).

## Workflow (GitHub Flow)
Short, clearly named branch → commits with descriptive messages → pull request (a draft for early feedback) → review and follow-up commits → merge once checks pass → delete the branch.

## GitHub Actions hardening
- **Pin every third-party action to a full-length commit SHA** taken from the action's own repository, not a fork; let Dependabot propose updates. Tags can be moved. In March 2026, attackers published a malicious Trivy release and force-pushed 76 of 77 `aquasecurity/trivy-action` tags to credential-stealing code (GHSA-69fq-xp46-6x23, CVE-2026-33634). If a pipeline ran a compromised action, rotate every secret it could reach.
- **Least-privilege token**: `permissions: contents: read` at the top of every workflow; grant more per job only where needed.
- **No long-lived cloud keys**: use OIDC federation (for example AWS IAM roles), with the trust condition limited to this repo, branch or environment.
- **Untrusted input** (PR titles, branch names, issue bodies) never goes inline in `run:` through `${{ }}`; pass it through `env:` and quote it.
- **Avoid `pull_request_target` and `workflow_run`** unless privileged context is required, and never check out untrusted PR code in them.
- **Production deploys** run in a protected environment with required reviewers (rule `ci-deploy`).
- **Self-hosted runners** are high risk; never use them on public repos.
- **Releases**: artifact attestations give signed build provenance (SLSA Build Level 2, Level 3 through a reusable workflow); consumers check with `gh attestation verify`. On private repos this may need a higher GitHub plan: check availability before relying on it.

Sources (checked 2026-11-04): docs.github.com (rulesets and available rules, protected branches, code owners, Dependabot, secret scanning and push protection, Actions secure use, OpenID Connect, artifact attestations, GitHub flow); GHSA-69fq-xp46-6x23.
