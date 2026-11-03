---
name: fintech-lending
description: Domain rules for Indian digital lending systems (NBFC/LSP, loan origination and servicing, ledgers, disbursal and collection, KYC/eKYC, bureau, account aggregator, eSign/eNACH, payment gateways and webhooks) under RBI Digital Lending Directions 2025 and the DPDP Act 2023. Use when designing or changing anything that moves money, computes loan amounts, stores borrower data, or integrates a lending vendor.
---

# Fintech lending engineering

Regulatory text changes. These are engineering defaults, not legal advice: when a rule decides behaviour (fees, cooling-off, data location, disclosures), confirm the current RBI/DPDP wording or the client's compliance owner and record the source in the project docs. Never guess money or compliance logic; ask.

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
- Disbursal and repayment flows go directly between the regulated entity's account and the borrower; LSP/pool accounts must not sit in the flow unless the compliance owner confirms the structure.

## Integrations (KYC, bureau, AA, eSign, eNACH, gateways, NBFC APIs)
- One adapter per vendor behind an interface, so vendors can be swapped (dual-vendor gateways are common here). Sandbox and production credentials kept separate; sandbox mode switchable by config, never by code edits.
- Every outbound call: timeout, bounded retries with backoff only for idempotent operations, request id, and response logged without PII.
- Webhooks: verify HMAC signature and timestamp, store the event id, process idempotently, respond fast and do work asynchronously, and reconcile against the vendor's report or status API daily.
- Money-moving calls (payout, refund, mandate debit) carry an idempotency key persisted before the call; on timeout, query status, don't retry blindly.
- Keep vendor payloads (bureau reports, AA data) encrypted, access-audited and retained only as long as policy allows.

## Borrower data (RBI DL Directions 2025 + DPDP Act 2023)
- Collect only what the purpose needs, with explicit, purpose-specific, logged consent; no access to phone contacts, media or call logs.
- The LSP stores only the minimal data its role requires; the regulated entity owns the data obligations. Confirm data location (India storage; offshore processing only under the Directions' conditions) for every vendor and cloud region.
- Never store full Aadhaar or biometrics; mask PAN, account numbers and phone numbers in UI and logs; KYC documents private with signed, expiring URLs.
- Publish and implement retention and deletion: scheduled purge or anonymisation jobs with evidence.
- Grievance redressal and disclosures (lender name, KFS, APR, cooling-off) are product requirements: build them as features with tests.

## Testing must include
Rounding and schedule golden tests, duplicate webhook delivery, out-of-order webhooks, vendor timeout during payout, double-click on disburse, concurrent repayments on one loan, authorization of borrower A reading borrower B, and reconciliation mismatch alerts.
