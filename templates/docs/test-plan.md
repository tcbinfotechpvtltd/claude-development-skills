# <Project> test plan, test cases and traceability

Informed by ISO/IEC/IEEE 29119-3 (test documentation), scaled down for a small team.

## 1. Plan
- **Scope**: what is tested and what is not.
- **Test types used**: from the eng-testing map (unit, integration, API, end-to-end, UAT, security, accessibility, load, ...) and why.
- **Environments and data**: where tests run (local, CI, UAT); synthetic or masked data only.
- **Entry and exit criteria**: what must be true to start UAT or release (for example no open Critical/High defects, all Must requirements verified).
- **Roles and schedule**: who tests what, and when.
- **Risks**: what could make testing incomplete.

## 2. Test cases
| ID | Requirement | Title | Type | Preconditions | Steps | Expected result | Automated in | Last result |
|---|---|---|---|---|---|---|---|---|
| TC-001 | REQ-001 | | unit / API / e2e / manual / UAT | | 1. … 2. … | | `tests/...::test_name` or "manual" | YYYY-MM-DD pass, build or commit |

## 3. Traceability matrix
Every requirement has at least one test case; every test case points to a requirement. An empty cell is a gap to fix or explain.

| Requirement | Design / ADR | Code (module) | Test cases | Latest result | User manual section |
|---|---|---|---|---|---|
| REQ-001 | | | TC-001 | pass (YYYY-MM-DD) | how-to/... |

## 4. Test completion report (one per release)
| Release | Date | Suites run (counts) | Manual / UAT cases run | Open defects by severity | Recommendation |
|---|---|---|---|---|---|
| vX.Y.Z | | | | | go / go with known issues / no-go |
