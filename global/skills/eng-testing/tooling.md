# Test tooling by stack, and cross-cutting checks

Use what the repo already has; introduce a framework only when there is none, and then the first one listed.

## By stack
| Stack | Unit and integration | End-to-end / UI | Notes |
|---|---|---|---|
| Python services | pytest 9 (Python 3.10+) | Playwright (Python or Node) | fixtures over setup code; `freezegun`-style time freezing |
| Frappe / ERPNext | `bench --site <test-site> run-tests --app <app>` with `FrappeTestCase` | Playwright against UAT | dedicated test site only (skill `frappe-erpnext`) |
| Odoo | `TransactionCase`, `HttpCase`, JS tours, `@tagged` | tours, Playwright | test database only (skill `odoo`) |
| PHP / CodeIgniter 3 | PHPUnit matched to the app's PHP version (12 needs 8.3+, 13 needs 8.4+; older PHP needs an older PHPUnit, see phpunit.de supported versions). Never raise PHP just to run tests. CI3's built-in Unit_test class is not a real test suite | Playwright | test controllers through HTTP; models against a test database |
| Next.js / TypeScript | Vitest 5 (Node 22.12+) or the repo's Jest 30 | Playwright (`@playwright/test`), including API tests with the `request` fixture | Testing Library for components |
| Flutter | `flutter test` (unit and widget); golden tests with `matchesGoldenFile`, `--update-goldens` | `integration_test` (ships with the SDK); `patrol` when native dialogs must be driven | test on a real device for camera, KYC and payment flows |

## Cross-cutting checks
- **Accessibility**: WCAG 2.2 level AA is the current W3C Recommendation (9 new success criteria since 2.1; WCAG 3.0 is still a draft). Run an automated checker in end-to-end tests, then check keyboard-only use and a screen reader on key flows.
- **Web performance**: the Core Web Vitals at the 75th percentile are LCP ≤ 2.5 s, INP ≤ 200 ms and CLS ≤ 0.1. Check them on the pages that matter (landing, apply, dashboard).
- **Load**: Grafana k6 2.x scripts. Baseline first, then target load and a spike; set thresholds on p95 latency and error rate. Run against UAT; production load tests need the user's approval.
- **Contracts**: Pact for consumer-driven contract tests between apps (spec v3 is the widely supported level; v4 is still beta in several languages).
- **Security scans**: Semgrep CE (static analysis), gitleaks (secrets), Trivy (dependencies and container images), ZAP by Checkmarx (dynamic baseline scan of UAT). Pin these tools to verified versions: in March 2026 a malicious Trivy release was published and the `trivy-action` tags were moved to credential-stealing code (GHSA-69fq-xp46-6x23).
- **Property-based and fuzz testing**: Hypothesis 6.170 (Python) and fast-check 4.10 (JS/TS) for invariants in calculations and parsers. Schemathesis 4.33 generates API test cases from an OpenAPI or GraphQL schema. Atheris 3.1 is a coverage-guided fuzzer for Python parsers (Python 3.11–3.14, Linux and macOS).
- **Accessibility and performance automation**: axe-core 4.14 through `@axe-core/playwright` 4.14 in end-to-end tests; Lighthouse 13 via Lighthouse CI (`@lhci/cli` 0.16) in the pipeline.
- **Test data**: Faker 40 (Python) and `@faker-js/faker` 10 for synthetic data, always with a fixed seed.
- **Test sizes** (Software Engineering at Google): small means one process with no network, disk or sleeps; medium means one machine, with localhost network allowed; large means several machines or a real environment. Keep most tests small.
- **Mutation testing** on critical modules only (interest, fees, ledger postings), to prove the tests catch real faults: StrykerJS (JS/TS), mutmut (Python), Infection (PHP).

Sources (checked 2026-11-04): w3.org/TR/WCAG22 and the WCAG 3.0 draft; web.dev/articles/vitals; playwright.dev; vitest.dev; jestjs.io; pypi.org (pytest, mutmut); phpunit.de supported versions; CodeIgniter 3 user guide; docs.flutter.dev/testing; grafana.com/docs/k6; docs.pact.io; zaproxy.org; semgrep, gitleaks, trivy and stryker releases; GHSA-69fq-xp46-6x23; PyPI and npm (Hypothesis, fast-check, Schemathesis, Atheris, Faker, axe-core, Lighthouse CI); abseil.io/resources/swe-book (ch. 11, test sizes).
