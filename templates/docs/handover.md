# Handover: <project> from <outgoing> to <incoming>, YYYY-MM-DD

Complete this before anyone leaves the project. The goal is that the next person can run, change and release the system without calling the previous one.

## Access
- [ ] Repository, CI, hosting, DNS, cloud, monitoring and vendor dashboards: incoming person added, outgoing person removed.
- [ ] Credentials the outgoing person knew are rotated; new values are only in the password manager or secret store.
- [ ] Client contacts introduced; who approves what is written down.
- [ ] Ownership of vendor accounts, domains, certificates and software licences moved to the company or client (never a personal account).

## Knowledge
- [ ] `docs/README.md` index reviewed: every document exists and is current.
- [ ] Requirements, test cases and the user manual match the current release.
- [ ] Runbook walked through together: deploy, roll back, restore.
- [ ] Open work: branches, PRs, half-done changes, promises made to the client.
- [ ] Known issues, technical debt and risks (RAID log) reviewed.
- [ ] Gotchas recorded in the project CLAUDE.md.
- [ ] `.env.example` lists every key; seed or demo data needed for development and screenshots is in the repo.
- [ ] Incident contacts and escalation in the runbook are current.

## Proof
- [ ] The incoming person set up the project from the README and ran the tests.
- [ ] The incoming person did one deploy to UAT using only the runbook.

Signed off by: <incoming>, <outgoing>, <project lead>
