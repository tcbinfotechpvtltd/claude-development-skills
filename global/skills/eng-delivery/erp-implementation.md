# ERP implementation method (ERPNext/Frappe and Odoo)

TCB's method, built from Frappe's partner implementation procedure, Odoo's implementation methodology, Microsoft's Success by Design and SAP Activate's fit-to-standard idea. Framework specifics are in skills `frappe-erpnext` and `odoo`; documents in skill `eng-docs`.

## Phases
| Phase | What happens | Exit (written, signed) |
|---|---|---|
| 1. Discover and plan | stakeholders; one client single point of contact (SPoC) with decision authority; an inventory of processes; phasing (smallest valuable scope first, for example sales, purchase and inventory in the first 1–2 months); budget, plan and RAID log; kick-off that walks the client through this method | project brief, `requirements.md` and `glossary.md` drafted, plan agreed |
| 2. Fit-to-standard and fit-gap | workshops on a demo of the standard product, process by process. Classify each requirement as **standard**, **configuration** (settings, workflows, print formats) or **customisation** (code). Customise only a real gap with business value | requirements baselined: the fit-gap column filled in `requirements.md` and the document signed by the client; solution design approved |
| 3. Build | configuration first, then customisation in a custom app or module (never core), then integrations. Iterate with key users: show, validate, adjust, every week. Review the data model, roles and permissions, integrations and testing at each milestone | demos accepted; test cases written against requirements |
| 4. Data migration | master data, opening balances and open transactions, not full history. Use the framework's import templates in batches (ERPNext Data Import: CSV or Excel, insert or update, notification emails off). The client's data owner cleanses the data. Do mock loads, at least one in testing and one in UAT, on a neutralized copy; rehearsals that need real data follow the restricted tier in skill `eng-testing` (test-types.md) | reconciliation signed by client finance: record counts, stock value, receivables and payables, trial balance against the old system |
| 5. UAT and training | UAT on migrated data that has been masked;  scenarios traced to requirements; key users trained first, then end users from the per-role user manual | written UAT sign-off; no open Critical or High defects |
| 6. Cutover and go-live | a cutover plan with tasks, owners, timings, checks and a rollback; mock cutovers rehearsed; a transaction freeze in the old system; a go/no-go meeting with agreed criteria; final migration and reconciliation; the old system retired or made read-only | go/no-go decision recorded; reconciliation signed |
| 7. Hypercare | extra support after go-live, typically 2–8 weeks (a month is common): daily check-ins in the first week, fast fixes, close watch on jobs and integrations. It ends on criteria (incidents falling, nothing critical open), not on a date | handover to support/AMC (Kanban, skill `eng-delivery`) with the handover pack |
| 8. Next phase | the remaining modules and improvements, usually starting about a month after go-live | a new plan and scope |

## Rules
- **Standard first.** Every customisation names its requirement id, says why standard and configuration cannot meet it, and notes its upgrade cost: custom code is what breaks in Odoo 17→20 or Frappe v15→v16 upgrades.
- **Configuration is versioned too.** Export it to the custom app or module (Frappe fixtures, Odoo data XML) so environments can be rebuilt and compared.
- **Decisions are written.** The SPoC confirms each decision in writing, recorded in `docs/decisions.md`. Undocumented verbal decisions become disputes at UAT.
- **Data**: never delay go-live waiting for perfect data, but never go live with unreconciled balances.
- **Neutralize every copy of a client database before starting it**, because otherwise it can email customers, run jobs and charge or message real people:
  - Odoo: `odoo-bin neutralize -d <copy>`.
  - Frappe: `bench --site <copy> set-config mute_emails 1`, then `bench --site <copy> disable-scheduler`, then clear the email account, payment gateway, SMS and integration credentials.
- **Indian statutory setup** (GST, e-invoicing, e-way bills, TDS and similar) is configured and tested with the client's accountant before go-live, using the providers' sandboxes.
- **Roles and permissions** come from the requirements, and each role is tested by logging in as it.
- **Training** comes from the user manual. A gap found in training is fixed in the manual.

Sources (checked 2026-11-04): frappe.io/partner-sop/implementation-procedure and frappe.io/partner/implementation; docs.frappe.io/erpnext (data import, getting started); Odoo implementation methodology guide; learn.microsoft.com Dynamics 365 Success by Design and cutover guidance; SAP Activate phases (via SAP LeanIX).
