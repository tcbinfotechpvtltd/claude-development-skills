# <Project> requirements

**Status**: draft | confirmed by <client name, role> on YYYY-MM-DD | changed (see section 10)
Write each requirement so it is necessary, about one need only, unambiguous, feasible and verifiable. Anything not yet confirmed by the client is marked **TO CONFIRM**.

## 1. Business context
- **Client and business goal**: <who they are, what they want to achieve>
- **Problem today**: <what hurts now, with numbers where possible>
- **Success measures**: <how the client will judge success: time saved, errors removed, revenue, compliance>

| User role | Who | What they need | Number of users |
|---|---|---|---|

## 2. Business processes
For each process: how it works today (as-is), how it will work with the system (to-be), and who does each step. A Mermaid flowchart helps for anything with branches.

## 3. Scope
- **In scope**:
- **Out of scope**:

## 4. Functional requirements
| ID | Requirement | Why / source (who, date) | Priority | Fit-gap (ERP) | Acceptance criteria | Status | Test cases |
|---|---|---|---|---|---|---|---|
| REQ-001 | The system shall … | | Must / Should / Could / Won't | standard / configuration / customisation | Given … when … then … | proposed / confirmed / built / verified | TC-001 |

## 5. Quality requirements
| Area | Requirement |
|---|---|
| Performance | <e.g. list pages load in under 2 s for 50 concurrent users> |
| Availability and backup | <uptime target, RPO/RTO> |
| Security and access | <roles, MFA, audit trail> |
| Compliance | <RBI, DPDP, GST, statutory reports> |
| Usability and accessibility | <devices, browsers, languages, WCAG level> |
| Data retention | <what is kept, for how long, then deleted or anonymised> |

## 6. Data and integrations
- Master data and its owners; data to migrate (source, volume, quality issues).
- External systems: name, purpose, direction, protocol, owner, sandbox available?

## 7. Reports, documents and notifications
| Output | Audience | Contents | Trigger or schedule |
|---|---|---|---|

## 8. Assumptions, constraints and dependencies

## 9. Open questions
| # | Question | Asked whom, when | Answer |
|---|---|---|---|

## 10. Change history
| Date | Change | Requested by | Approved by | Change request |
|---|---|---|---|---|
