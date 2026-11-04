---
name: eng-project-init
description: Create or refresh a project's CLAUDE.md, path-scoped .claude/rules and progress file from the eng-os template by inspecting the repository. Use for a repo or project folder with no CLAUDE.md, when the user asks to set up or onboard a project, or when a project's CLAUDE.md is stale or bloated.
argument-hint: "[project path]"
---

# Project initialisation

Goal: a concise project CLAUDE.md (target under 120 lines) that lets any future session work correctly without re-exploring the codebase. It complements the global standards; it never repeats them.

## 1. Discover (read-only, cheaply)
Work from the project root given as the argument (default: the current project).
- Stack and versions: manifests (`package.json`, `composer.json`, `pyproject.toml`/`requirements*.txt`, `pubspec.yaml`, `__manifest__.py`, `hooks.py` + `modules.txt` for Frappe), lockfiles, `.nvmrc`/`.python-version`, Dockerfiles.
- Commands: scripts in manifests, `Makefile`, `Procfile`, CI workflows, README. Prefer commands CI actually runs.
- Architecture: top two directory levels (`ls`, `find -maxdepth 2 -type d`, excluding vendor/node_modules), entry points, route files, integration adapters.
- Environments: branches (`git branch -a`), CI deploy jobs, deploy scripts, env templates (key names only, never values).
- Existing knowledge: README, docs/, existing CLAUDE.md or AGENTS.md, the user's memory notes about this project.
- Large repo (hundreds of files you would need to skim): delegate the survey to one `Explore` subagent with `model: sonnet` and a brief asking for exactly the template sections; keep only its conclusions.

## 2. Write
- Start from `~/.claude/eng-os/templates/project/CLAUDE.md`. Fill every section from evidence. Leave a section out rather than writing guesses; list genuine unknowns under "Open questions" for the user.
- **Required skills** line: choose from the global skill list by domain and stack (for example a Frappe lending app gets `eng-security, fintech-lending, frappe-erpnext`; an Odoo implementation `odoo`; a Next.js, CodeIgniter 3, Flutter or Python app `custom-apps`; any client project with a scope and deadlines `eng-delivery`).
- Invariants: only rules specific to this project (business rules, tenancy, data ownership). Global rules stay global.
- If an existing CLAUDE.md exists: preserve its project knowledge, remove what duplicates the global file, and fix what is stale. Show the user the diff summary.
- Path-specific guidance in a big repo (for example migrations, a legacy module, generated code) goes to `.claude/rules/<topic>.md` with `paths:` frontmatter, so it loads only when those files are touched.
- Personal, machine-specific notes (local ports, credentials locations) go to `CLAUDE.local.md`, which must be gitignored.
- Long-running effort: create `docs/progress.md` with Goal / Decisions / Done / Next / Risks.

## 3. Check
- No secrets or credential values anywhere in the written files.
- Every command listed was run or is confirmed by CI config; mark unverified ones `(unverified)`.
- Line count under ~120; nothing copied from the global CLAUDE.md.
- Tell the user which files were created or changed. Committing them follows the project's normal git rules.
