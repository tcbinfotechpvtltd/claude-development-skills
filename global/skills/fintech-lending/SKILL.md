---
name: fintech-lending
description: Domain rules for Indian digital lending systems (NBFC/LSP, loan origination and servicing, ledgers, disbursal and collection, KYC/eKYC, bureau, account aggregator, eSign/eNACH, payment gateways and webhooks) under RBI Digital Lending Directions 2025, RBI NBFC cyber/IT and outsourcing directions, and the DPDP Act 2023 with DPDP Rules 2025. Use when designing or changing anything that moves money, computes loan amounts, stores borrower data, or integrates a lending vendor.
---

# Fintech lending engineering

Regulatory text changes. These are engineering defaults, not legal advice: when a rule decides behaviour (fees, cooling-off, data location, disclosures), confirm the current RBI/DPDP wording or the client's compliance owner and record the source in the project docs. Never guess money or compliance logic; ask.
Rules below were checked against RBI and DPDP sources on 2026-11-04. RBI consolidated its instructions into Master Directions on 28 Nov 2025: the digital lending rules are restated in Chapter III of the NBFC (Credit Facilities) Directions 2025 with the same values. Which text governs a given client is its compliance owner's call.

## Money and ledgers
- Amounts in integer paise or fixed DECIMAL(18,2+) in the database; Decimal in code (Python `Decimal`, PHP `bcmath`/integer paise, JS integer paise or a decimal library). Never binary floats for money.
- Store currency with every amount. Round once, at the point the business rule defines, with a named rounding mode (half-up vs banker's); test the boundaries.
- Ledgers are append-only double entry: every movement has balanced debit and credit lines; corrections are reversing entries, never UPDATE or DELETE of posted lines.
- Balances are derived from the ledger (or a materialised balance updated in the same transaction with a row lock). Reconcile derived balances against the ledger in tests and in a scheduled job.
- Interest, penal charges and DPD: explicit day-count convention, IST business dates computed from UTC timestamps, holiday handling documented; golden-master tests for the schedule.
- Fees and APR shown to the borrower come from the same calculation the ledger uses (Key Fact Statement consistency).

## Lifecycles
- Application, KYC, underwriting, sanction, agreement/eSign, disbursal, repayment, collection and closure are explicit state machines; invalid transitions are rejected server-side and every transition is logged (who, when, from, to, reason).
- Disbursal only after all gates pass on the server: KYC verified, sanction approved, agreement signed, cooling-off/consent rules satisfied, bank account verified (penny drop), and no duplicate disbursal for the loan (unique constraint + idempotency key).
- Fund flows: disbursal only into the borrower's own bank account; repayment straight into the regulated entity's (RE) account; no LSP, pool or third-party pass-through account in either direction, and the LSP never controls the flow. The RE, not the borrower, pays the LSP's fees. Any exception needs the RE compliance owner's written confirmation.
- No automatic credit-limit increase: only on an explicit, recorded borrower request.
- Cooling-off (look-up) period: length set by the RE's board, at least one day. Build the exit flow and its charges exactly as the RE's policy states.

## Integrations (KYC, bureau, AA, eSign, eNACH, gateways, NBFC APIs)
- One adapter per vendor behind an interface, so vendors can be swapped (dual-vendor gateways are common here). Sandbox and production credentials kept separate; sandbox mode switchable by config, never by code edits.
- Every outbound call: timeout, bounded retries with backoff only for idempotent operations, request id, and response logged without PII.
- Webhooks: verify HMAC signature and timestamp, store the event id, process idempotently, respond fast and do work asynchronously, and reconcile against the vendor's report or status API daily.
- Money-moving calls (payout, refund, mandate debit) carry an idempotency key persisted before the call; on timeout, query status, don't retry blindly.
- Keep vendor payloads (bureau reports, AA data) encrypted, access-audited and retained only as long as policy allows.

## Borrower data (RBI DL Directions 2025 + DPDP Act 2023 and Rules 2025)
- Collect only what the purpose needs, with prior explicit, purpose-specific consent and an audit trail. Apps never access files, media, contacts or call logs; camera, microphone and location only once, for onboarding.
- The LSP stores only the minimal data its role requires; the RE owns the data obligations. Data is stored in India; anything processed abroad is deleted there and brought back within 24 hours. Check this for every vendor and cloud region.
- DPDP Rules 2025 phases: consent-manager rules from 13 Nov 2026; notice, consent, security, breach, retention and rights duties from 13 May 2027. Build to them now: standalone itemised notice with links to withdraw consent, exercise rights and complain; breach intimation to the Data Protection Board and affected users without delay, with a detailed report to the Board within 72 hours; personal-data processing logs kept at least 1 year (longer than CERT-In's 180 days); rights requests answered within 90 days at most; age check at onboarding (under-18s need verifiable parental consent).
- Never store full Aadhaar or biometrics; mask PAN, account numbers and phone numbers in UI and logs; KYC documents private with signed, expiring URLs.
- Publish and implement retention and deletion: scheduled purge or anonymisation jobs with evidence.
- Grievance redressal and disclosures are product requirements, built as features with tests: lender name, KFS and APR per RBI's KFS circular of 15 Apr 2024 (one KFS link per offer), cooling-off terms, a nodal grievance officer at the RE and at any borrower-facing LSP, and escalation to the RBI Integrated Ombudsman (CMS portal) when a complaint is unresolved after 30 days.
- Recovery: the borrower is told the recovery agent's details by email or SMS before the agent's first contact.
- An LSP showing several lenders (from 1 Nov 2025): show every matching offer, name lenders that did not match, use a documented and consistent matching method, no dark patterns.
- Every digital lending app or site is reported by the RE on RBI's CIMS portal and updated on change: tell the client before launching a new app, domain or LSP.
- Default loss guarantee (DLG) arrangements are capped at 5% of the portfolio disbursed, as cash, a lien-marked FD or a bank guarantee.

## Technology vendor obligations (we are the NBFC's tech or outsourcing provider)
RBI's NBFC Cybersecurity, Technology: Risk, Resilience and Assurance Framework Directions 2026 (31 Jul 2026) and NBFC Managing Risks in Outsourcing Directions 2025 (28 Nov 2025) bind the NBFC and flow down by contract: expect audit and inspection rights, incident reporting to the NBFC, data location, access control, BCP and exit clauses. Keep the evidence (logs, access reviews, patch and backup records) ready. CERT-In 6-hour incident reporting also applies: see the eng-security skill's [standards.md](../eng-security/standards.md).

## Testing must include
Rounding and schedule golden tests, duplicate webhook delivery, out-of-order webhooks, vendor timeout during payout, double-click on disburse, concurrent repayments on one loan, authorization of borrower A reading borrower B, and reconciliation mismatch alerts.
