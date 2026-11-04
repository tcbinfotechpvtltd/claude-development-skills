# PHP / CodeIgniter 3

## Status (checked 2026-11-04)
- **CodeIgniter 3 is legacy.** The last release was 3.1.13 (March 2022); its maintainers say it gets "mostly just security updates", and there is no official end-of-life date. It officially targets old PHP versions, and its compatibility with PHP 8.2+ is not officially stated, so test on the target PHP version before any upgrade.
- **PHP versions**:
  - 8.2 gets security fixes only until 2026-12-31;
  - 8.3 until 2027-12-31;
  - 8.4 until 2028-12-31;
  - 8.5 until 2029-12-31.
  - A CI3 app on an unsupported PHP version is a security finding.
- **CodeIgniter 4** is the maintained line (4.7, PHP 8.2+ with `intl` and `mbstring`; only the latest version is maintained). New modules or a rewrite go through an ADR; never mix the two frameworks in one request path.

## Structure
- **Controllers** stay thin: input, authorization, a call into a model or library, then the response.
- **Models** own the database work, through Query Builder or `query($sql, $binds)` with bindings.
- **Libraries** hold vendor integrations, one adapter per vendor, with timeouts and logging without personal data.
- **Helpers** hold pure functions only.
- **Configuration per environment** under `application/config/<ENVIRONMENT>/`. Keys go in environment variables or a git-ignored keys file that is never committed.
- **Schema changes** use the repo's migration mechanism, numbered and reviewed (rule `db-migrations`). No ad-hoc SQL on shared databases.
- **Composer**: commit `composer.lock` and run `composer audit` before adding or upgrading.

## Working safely in a legacy codebase
- Read the surrounding code first: legacy apps often hide business rules in views, helpers and cron scripts.
- Characterise behaviour with tests before refactoring: PHPUnit against a test database, or HTTP-level tests ([tooling.md](../eng-testing/tooling.md)). CI3's `Unit_test` class is not a test suite.
- Apply the PER Coding Style only to new and changed code ([coding-standards.md](../eng-review/coding-standards.md)); reformatting whole files buries the real diff.
- Risk controls while on CI3:
  - `ENVIRONMENT=production` on live servers;
  - CSRF on;
  - uploads outside the web root;
  - a WAF or minimal exposure for admin paths;
  - the security checklist in [stacks.md](../eng-security/stacks.md).

Sources (checked 2026-11-04): github.com/bcit-ci/CodeIgniter README; codeigniter.com/userguide3 (changelog, requirements, unit testing); codeigniter4 releases and requirements; php.net/supported-versions.php.
