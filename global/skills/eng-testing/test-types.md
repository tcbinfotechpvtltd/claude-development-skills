# Test types: what each one catches and when to use it

Choose by risk. Every change gets the fast layers; slower ones are added for what the change touches. Tool versions are in [tooling.md](tooling.md); browser checks by Claude are in [browser.md](browser.md).

## Minimum per change (default; projects may require more)
- **Any code**: static checks, plus unit tests for the changed logic, plus a run of the relevant suite.
- **Data access or permissions**: integration tests against a real test database, including the denied cases.
- **New or changed endpoint**: API tests for authentication, validation, error shape and status codes.
- **UI change**: Claude checks it in a browser, plus component tests where the repo has them; end-to-end tests for the key journeys it touches.
- **Money, KYC or ledgers**: golden tests, property-based tests for calculations, and duplicate, replay and concurrency tests (skill `fintech-lending`).
- **Migration**: up, down and re-run on a production-like copy, with record counts and totals reconciled.
- **Release**: the full regression suite in CI, then a smoke test after the deploy.

## The map
| Type | What it catches | When | How |
|---|---|---|---|
| Static checks | type errors, typos, unsafe patterns | every change | the repo's linter, formatter and type checker ([coding-standards.md](../eng-review/coding-standards.md)) |
| Unit | logic errors in one function or class | every business rule, calculation, state transition and bug fix | no network, disk or database; milliseconds each |
| Component / widget | a UI piece misbehaving on its own | forms and reusable components | Testing Library, Playwright component tests, Flutter widget tests |
| Integration | wrong SQL or ORM use, transactions, permissions | data access, permissions, jobs, migrations | a real test database or site, never a client one |
| API | wrong status codes, auth gaps, inconsistent errors | every endpoint | Playwright `request` or pytest with an HTTP client; Schemathesis generates cases from an OpenAPI spec |
| Contract | a provider breaking an app that depends on it | APIs used by the mobile app, an NBFC or a partner | Pact |
| End-to-end | broken journeys across the whole stack | a few key journeys (login, apply, KYC, pay, disburse) | Playwright on local or UAT |
| Visual regression | unintended layout or style changes | design systems, printed documents (invoices, KFS, reports) | Playwright screenshot comparison; baselines made on the same OS and browser as CI |
| Browser check by Claude | a change that "passes" but looks or behaves wrong; console and network errors | every UI change before calling it done | [browser.md](browser.md) |
| Exploratory | what nobody thought to script | new features, before UAT | time-boxed charter: goal, area, notes, bugs found; turn each bug into a test |
| Smoke | a deploy breaking the basics | after every deploy, UAT and production | a short tagged subset; read-only in production |
| Regression | old bugs returning | every merge, in CI | the full automated suite; every fixed bug adds a test |
| Acceptance / UAT | building something other than what was asked | before client sign-off | scenarios traced to acceptance criteria (skill `eng-delivery`) |
| Accessibility | keyboard, screen-reader and contrast failures | every user-facing UI | automated axe checks in end-to-end tests, plus a manual keyboard and screen-reader pass (WCAG 2.2 AA) |
| Web performance | slow pages | landing, apply and dashboard pages | Lighthouse CI in the pipeline; Core Web Vitals from real users |
| Load, stress, soak, spike | capacity limits, memory leaks, queue backlogs | before launch, campaigns and bulk imports | k6 on UAT: expected load, beyond it (stress), hours long (soak), sudden bursts (spike) |
| Security | vulnerabilities | static analysis, dependency and secret scans on every PR; dynamic scan before release; a penetration test yearly or after major change | Semgrep, dependency audits, gitleaks, Trivy, ZAP; negative tests from skill `eng-security` |
| Property-based | edge cases humans miss | interest and EMI schedules, rounding, parsers, validators | Hypothesis or fast-check asserting invariants (instalments sum to principal plus interest; balance never negative) |
| Fuzzing | crashes and hangs on malformed input | file uploads, parsers, webhook handlers | Schemathesis for APIs; a coverage-guided fuzzer for parsers |
| Mutation | tests that would never fail | critical money modules | Stryker, mutmut, Infection |
| Migration and reconciliation | data lost or corrupted in a move | every schema or data migration, imports, go-live | rehearsal on a copy; counts, sums and sample records compared before and after |
| Backup restore and DR drill | backups that cannot be restored | on a schedule (for example quarterly) and before risky changes | restore into a scratch environment and check the data |
| Resilience | bad behaviour when a dependency fails | KYC, bureau, payment and NBFC integrations, queues | stubs returning timeouts, 5xx, garbage, duplicates and out-of-order events; kill a worker mid-job |
| Compatibility | works on one browser or device only | public web and mobile apps | Playwright on Chromium, Firefox and WebKit; a low-end Android phone and an iPhone; the oldest OS versions supported |
| Time and locale | date and number bugs | anything with dates, money or schedules | IST and UTC, month end, leap years, Indian number formats (lakh, crore), translations |
| Production checks | outages users would hit first | critical public flows | scheduled read-only probes with alerts (skill `eng-ship`) |

## Test data
- Synthetic data from factories or builders (Faker); never real personal data in tests, and only masked data in UAT.
- Fixed random seeds and frozen time; each test creates and cleans up its own data.
- A separate test database or site; tests never run against client or production data.
- Golden datasets for money calculations, reviewed by someone who owns the business rule.
