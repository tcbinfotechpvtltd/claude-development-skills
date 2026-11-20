# Security policy

eng-os runs a guard and hooks inside every Claude Code session on the machines that install it, so a flaw here can weaken a safety check everywhere at once.

## Reporting a vulnerability
Report it privately on GitHub: open the repo's **Security** tab and choose **Report a vulnerability**. Do not open a public issue or pull request for it. The maintainer replies in that private advisory.

In scope:
- a command or tool call the guard should ask about or deny but lets through;
- secrets or personal data written to a log, state file or backup;
- an install or update path that could run code from outside a tagged release.

## Supported versions
Only the latest release. Fixes ship as a new patch release, and `bash ~/.eng-os/install.sh` moves an install to it.
