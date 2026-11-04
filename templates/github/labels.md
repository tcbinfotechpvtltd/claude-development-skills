# Standard labels (create once per repo)

| Label | Meaning | Used by |
|---|---|---|
| `bug` | something broken | issue form, release notes "Fixes" |
| `feature` | new or changed behaviour | issue form, release notes "Features" |
| `security` | security fix or hardening | release notes "Security" |
| `breaking-change` | needs action from users or integrators | release notes "Breaking changes" |
| `migration` / `config` | database migration or new config keys | release notes, deploy checklist |
| `change-request` | outside the agreed fixed scope (needs written approval) | skill eng-delivery |
| `P0` `P1` `P2` `P3` | priority: now / this release / next / some day | planning |
| `blocked` | waiting on someone outside the team | status reports |
| `skip-changelog` | no release-notes entry (CI, typos) | release notes |

Severity (set by the reporter, from the issue form) is impact; priority (set by the lead) is urgency. Default mapping: Critical → `P0`, High → `P1`, Medium → `P2`, Low → `P3`; the lead may change priority with a reason.

Milestones: one per release (`v1.4.0` or `Release 2026-11-15`). Pull requests close their issue with `Fixes #123` in the description.
