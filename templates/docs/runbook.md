# <Project> runbook

For whoever operates the system, including someone who has never seen it. Never write secret values here: say where they live.

## Environments
| Environment | URL | Server / account | Branch | Deployed by |
|---|---|---|---|---|
| UAT | | | | |
| Production | | | | |

## Access
- Where credentials live: <password manager vault / secret store path>, and who can grant access.
- SSH or console access: <how, from where, and who approves>.

## Deploy
1. <exact commands or CI job, in order>
2. <post-deploy checks: smoke tests, logs, metrics>

## Roll back
- Code: <previous tag or artifact and how to redeploy it>.
- Database: <migration down, or restore steps>; when to choose a restore over a down migration.

## Backups and restore
- What is backed up, how often, where, and how long it is kept.
- Restore procedure, step by step, and the date of the last successful restore test.

## Scheduled jobs and integrations
| Job / integration | Schedule or trigger | What it does | If it fails |
|---|---|---|---|

## Monitoring and alerts
| Alert | Meaning | First steps |
|---|---|---|

## Common incidents
### <Symptom>
- Likely cause:
- How to confirm:
- Fix:
- Prevent:

## Contacts and escalation
| Role | Name | Contact | When to call |
|---|---|---|---|
