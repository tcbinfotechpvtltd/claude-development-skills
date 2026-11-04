# Coding standards by language

Order of authority: (1) the repo's own formatter and linter config and the style of the surrounding code; (2) the language's official guide below; (3) conventions in the project CLAUDE.md. Format only what you change; reformatting untouched code goes in its own PR.

## Every language
- Names say what a thing is or does; no abbreviations a newcomer would not know.
- Functions do one thing; early returns instead of deep nesting; no magic numbers (named constants).
- Business rules as small pure functions that are easy to test; I/O at the edges.
- Errors handled where something useful can be done, with context; never swallowed. Validate at system boundaries.
- Comments explain why; public functions and modules have a short docstring or doc comment.
- No dead or commented-out code, no debug output, no new global mutable state.
- Logs carry context (request id, entity id) and never secrets or full personal data.

## By language
| Language | Official guide | Format | Lint / static checks |
|---|---|---|---|
| Python (incl. Frappe, Odoo) | PEP 8 (living document); Odoo modules follow the Odoo coding guidelines (skill `odoo`) | `ruff format` only where the repo has a ruff config (Frappe repos do: tabs, line length 110, double quotes); never reformat an Odoo or legacy codebase wholesale | `ruff check` (Ruff 0.17 replaces flake8, isort and Black) |
| PHP (CodeIgniter 3, others) | PHP-FIG PER Coding Style 3.1 (extends and replaces PSR-12) | PHP-CS-Fixer `@PER-CS` is the source of truth for style | PHP_CodeSniffer 4 only if the repo already uses it, configured not to fight the fixer; a static analyser such as PHPStan where the project has one. Legacy CI3: apply to new and changed code only |
| TypeScript / JavaScript | TypeScript handbook; typescript-eslint configs | Prettier 3 | ESLint 10 with flat config (`eslint.config.js`) plus typescript-eslint 8 `recommended-type-checked` (`strict-type-checked` for new projects); `strict` on in `tsconfig.json` |
| Dart / Flutter | Effective Dart (style, documentation, usage, design) | `dart format` | `flutter analyze` / `dart analyze` clean with `flutter_lints` 6 (apps) or `lints` 6 recommended (packages) |
| SQL | parameterised always; explicit column lists; keywords upper case | formatter of the repo, if any | review every query plan on hot paths |

## Automate it
- New repos we own: a `pre-commit` config that runs the formatter and linter, the same checks in CI, and CI failing on lint errors.
- Frappe's own repo runs ruff (lint, import sort, format), ESLint, Prettier and commitlint (Conventional Commits) through pre-commit: mirror that in Frappe apps.

Sources (checked 2026-11-04): peps.python.org/pep-0008; docs.astral.sh/ruff; php-fig.org/per/coding-style; PHP-CS-Fixer rule sets; PHP_CodeSniffer releases; typescript-eslint.io/users/configs; eslint.org; prettier.io; dart.dev/effective-dart; pub.dev lints and flutter_lints; frappe/frappe pre-commit and pyproject config.
