# Versioning, commits, branches, changelogs and release notes

A repo's existing convention wins (for example date tags such as `release-YYYY-MM-DD`). Use these defaults for new repos and repos without a convention, and record the choice in the project CLAUDE.md.

## Versioning (SemVer 2.0.0)
- Declare what the public API is: endpoints, request/response and webhook schemas, config keys, CLI flags, exported library functions.
- `MAJOR.MINOR.PATCH`: MAJOR for any incompatible API change, MINOR for compatible new functionality or a deprecation, PATCH for compatible bug fixes only. Lower parts reset to 0.
- A released version is never modified; any change ships as a new version. Pre-releases use `-rc.1`, `-beta.2`.
- Deployed apps with no external consumers (a client ERP, a website) may use date tags instead; pick one scheme per repo.
- Where versions live: Frappe app `<app>/__init__.py` `__version__`; Flutter `pubspec.yaml` `version: x.y.z+build` (build number always increases); Node `package.json`; Python `pyproject.toml`.

## Commits (Conventional Commits 1.0.0)
- `type(scope)!: description`, then a blank line, a body that explains why, and optional `Token: value` footers.
- The spec itself defines `feat` (new feature, maps to MINOR) and `fix` (bug fix, maps to PATCH). Common extra types (commitlint conventional config): `build chore ci docs style refactor perf test revert`.
- Breaking change: `!` right before the colon and/or a `BREAKING CHANGE: <what and how to migrate>` footer (uppercase). Maps to MAJOR.
- Use it in repos we own or that already use it; follow the existing style in client repos. One logical change per commit.
- Commit messages carry no customer or client names, personal data, email addresses or pasted ticket text: they outlive the ticket and can become public.

## Branches and pull requests
- Short-lived branches: about two days at most, including review wait. One branch in flight per developer (or developer plus agents). Merge trunk into the branch freely; merge the branch to trunk once when done, then delete it. Never merge into someone else's branch.
- Small PRs (Google eng-practices): one self-contained change. About 100 lines is reasonable and about 1000 usually too large. Refactors go in their own PR; tests, and a caller for any new API, go in the same PR. Don't break the build between dependent PRs.
- PR template: `.github/pull_request_template.md` (or repo root or `docs/`); several templates go in `.github/PULL_REQUEST_TEMPLATE/`. GitHub only uses a template once it is on the default branch. Starter: `~/.claude/eng-os/templates/release/pull_request_template.md`.

## Changelog (Keep a Changelog 1.1.0)
- File `CHANGELOG.md`, written for humans, never a dump of the git log. Latest version first; every version has an entry and a date (`YYYY-MM-DD`).
- `## [Unreleased]` at the top collects changes as they merge; at release time move them under `## [x.y.z] - YYYY-MM-DD`.
- Group entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Link each version heading to its compare view. Mark pulled releases `[YANKED]`. State whether the project follows SemVer.
- Starter: `~/.claude/eng-os/templates/release/CHANGELOG.md`.

## GitHub release notes
- Auto-generated notes are configured by `.github/release.yml`: `changelog.categories[]` with a required `title` and `labels` (`"*"` catches all remaining PRs), optional per-category `exclude`, and top-level `changelog.exclude.labels` / `.authors`. Categories only work if PRs carry labels. Starter: `~/.claude/eng-os/templates/release/release.yml`.
- Always review and edit generated notes before publishing. Notes for clients and devops must state: user-visible changes, breaking changes with required actions, migrations, new or changed config/env keys (names only), security fixes (no exploit detail before users can patch), the rollback target (previous tag) and known issues.

## Release procedure
1. All changes merged and CI green on the release commit.
2. Move `Unreleased` entries into the new version section; bump the version files.
3. Annotated tag on the merged commit: `git tag -a vX.Y.Z -m "vX.Y.Z"` (or the repo's scheme).
4. Pushing the tag and `gh release create` are outward-facing: the user approves them (the guard asks).
5. Deploy with the release checklist in the eng-ship skill; the release notes name the rollback target.

Sources (checked 2026-11-04): semver.org; keepachangelog.com/en/1.1.0; conventionalcommits.org/en/v1.0.0; docs.github.com (automatically generated release notes; pull request templates); trunkbaseddevelopment.com/short-lived-feature-branches; google.github.io/eng-practices/review/developer/small-cls.html.
