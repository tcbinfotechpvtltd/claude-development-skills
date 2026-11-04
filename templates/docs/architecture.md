# <Project> architecture

Based on the arc42 template (v9.1), shortened: fill what helps a newcomer and delete the rest. Diagrams follow the C4 model in Mermaid.

## 1. Introduction and goals
The essential requirements (link `requirements.md`), the top 3 quality goals, and the stakeholders who care about the architecture.

## 2. Constraints
Technical, organisational and regulatory constraints (framework, hosting, RBI or DPDP, client policies).

## 3. Context and scope
A system context diagram: users and external systems (KYC, bureau, payments, NBFC, email, SMS), with what flows between them.

## 4. Solution strategy
The key technology choices and why, in a few bullets.

## 5. Building block view
A container diagram (apps, databases, queues, workers), then the main modules with one line of responsibility each.

## 6. Runtime view
Sequence diagrams for the 2–4 flows that matter most (for example apply → KYC → sanction → disbursal, or order → invoice → payment).

## 7. Deployment view
Environments, servers or cloud services, network boundaries, and where each container runs.

## 8. Crosscutting concepts
Authentication and authorization, multi-tenancy or multi-company, error handling, logging and audit, money handling, time zones, configuration, background jobs.

## 9. Architecture decisions
The index of `adr/` records.

## 10. Quality requirements
Measurable scenarios, for example "a disbursal webhook delivered twice creates one payout".

## 11. Risks and technical debt
Known risks and debt, each with impact and the plan.

## 12. Glossary
See `glossary.md`.
