---
name: eng-testing
description: Test strategy, test-first bug fixing and systematic root-cause debugging. Use when writing or fixing tests, when a test, build or deploy fails, when behaviour differs from expectations, for flaky tests, or when deciding what and how much to test.
---

# Testing and debugging

## What to test (risk-based, not coverage-chasing)
- **Always**: business rules and calculations (money, interest, tax, eligibility, dates), state transitions, authorization (allowed and denied paths), input validation, every fixed bug, integration adapters (with recorded or sandbox responses).
- **Usually**: API contracts (request/response shape, status codes, error shape), migrations (up, down, re-run), critical UI flows end-to-end (login, apply, pay).
- **Rarely**: trivial getters, framework behaviour, generated code.
- Shape (test pyramid): many fast unit tests, fewer integration tests against a real DB, a handful of end-to-end tests for key journeys only. Push each test as low as it can go; when a higher-level test catches a bug, add a lower-level test for it; delete higher-level tests that only duplicate lower ones. Coverage is a signal for gaps, not a target; changed business logic should be covered.
- Another team or app consumes the API (mobile app, NBFC, partner): add consumer-driven contract tests (e.g. Pact) that the provider runs in its pipeline.
- Security tests: negative cases from skill `eng-security`; for audits use the OWASP WSTG v4.2 test cases and ASVS 5.0 requirements as pass/fail criteria.

## Writing good tests
- One behaviour per test, named for the behaviour (`test_disbursal_rejected_when_kyc_pending`).
- Arrange-act-assert (or given-when-then); assert observable behaviour, not implementation details; prefer readable tests over DRY ones.
- Deterministic: freeze time, seed randomness, no network to real vendors, no ordering dependence; isolated data per test (transactions or fixtures).
- Boundary cases: zero, negative, max, empty, null, unicode, duplicate submission, concurrent update, timezone edges (IST vs UTC, month end, leap year).
- Use the project's existing framework and helpers (pytest, `bench run-tests`, PHPUnit, Jest/Vitest, Playwright, flutter_test). Don't introduce a second framework.

## Bug fix protocol (prove it)
1. Reproduce: get the exact error, input and environment. Write the smallest failing test or script that shows it.
2. Fix the root cause, not the symptom.
3. The test now passes; the full relevant suite still passes.
4. Ask: where else could the same defect exist? Grep for the pattern and fix or report siblings.

## Root-cause debugging
1. **Read the evidence first**: full error message, stack trace, logs around the timestamp (`tail -200`, grep the request id). Read the code at the failing line.
2. **Characterise**: always or intermittent? Since when (`git log -p`, `git bisect` for regressions)? Which environment? What changed (deploy, config, data, dependency)?
3. **Hypothesise**: list two or three candidate causes with the evidence for each. Rank by likelihood times cheapness of testing.
4. **Test one hypothesis at a time** with a decisive experiment (log line, breakpoint, minimal repro, query). Change one variable per experiment.
5. **Fix, verify, prevent**: regression test, and a guard (validation, constraint, alert) if the failure class can recur.
- Two failed fix attempts means the model of the problem is wrong: go back to step 1, don't keep patching.
- Never "fix" by catching and ignoring the exception, adding sleeps, raising timeouts blindly, or deleting the failing test.

## Flaky tests
Quarantine only with a tracking note; find the nondeterminism (time, order, shared state, async waits, network). Replace sleeps with explicit waits on conditions.

## Reporting
State which suites ran, the counts (passed/failed/skipped), and paste the failure output for anything red. "Tests pass" without a run is not acceptable.

Sources (checked 2026-11-04): martinfowler.com/articles/practical-test-pyramid.html; owasp.org WSTG v4.2 (stable; 5.0 in progress).
