# <Product> user manual

For: <roles>. Matches release <vX.Y.Z> (YYYY-MM-DD). What changed: [What's new](whats-new.md).

The manual follows the Diátaxis framework: four kinds of page, never mixed on one page.

| Section | Kind | For | Example pages |
|---|---|---|---|
| Getting started | tutorial | a new user learning by doing | first login; your first loan application from start to finish |
| How-to guides | task steps | a user who knows what they want to do | how to approve a loan; how to export the monthly report (one task per page, grouped by role) |
| Reference | facts | a user looking something up | each screen's fields and rules; statuses and what they mean; roles and permissions; error messages |
| Explanation | concepts | a user who wants to understand why | the loan lifecycle; how approvals are routed; why KYC steps exist |
| Administration | how-to and reference | client admins | users and roles, masters and settings, scheduled jobs |

## Writing rules
- **Voice**: second person and active voice ("Select **Submit**"), with the condition before the instruction ("To cancel, select **Cancel**").
- **Steps**: numbered, one action each, and say what the user should see afterwards.
- **Words**: the exact screen labels and the glossary terms; sentence-case headings.
- **Screenshots**: only where they help, taken from UAT with synthetic data and alt text on every image. Never real customer data or secrets. Refresh them at each release.
- **Updates**: every user-visible change updates its how-to and reference pages in the same pull request, and adds a line to "What's new".
