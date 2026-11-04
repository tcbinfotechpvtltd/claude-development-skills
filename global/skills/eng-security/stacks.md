# Stack-specific security pitfalls

## Frappe / ERPNext
- Whitelisted methods are public API: check `frappe.has_permission(doctype, ptype, doc)` or `frappe.only_for(roles)` first. `frappe.get_doc(...).save()` respects permissions; `frappe.db.set_value`, `frappe.db.sql` and `ignore_permissions=True` bypass them.
- `allow_guest=True` endpoints: validate every argument, rate-limit (`@rate_limit`), never return documents wholesale.
- Use `frappe.get_list` (permission-aware) rather than `frappe.get_all` (ignores permissions) when results reach a user.
- Jinja in print formats/web pages: `{{ value }}` is escaped in web templates, but `| safe` and HTML fields render raw; sanitize with `frappe.utils.html_utils.clean_html`.
- File doctype: `is_private=1` for KYC and financial documents; public files are world-readable by URL.
- Keep Server Scripts and System Console off in production; restrict `Administrator`; enforce strong password policy and 2FA for System Managers; rotate the Administrator password after any suspected breach (see the Aug-2026 office ERPNext incident).
- `site_config.json` holds the DB password and `encryption_key`; never commit or print it; losing `encryption_key` makes Password fields unrecoverable.

## PHP / CodeIgniter 3
- Query Builder or `$this->db->query($sql, $binds)` with bindings; never interpolate `$_GET`/`$_POST`/`$this->input` into SQL.
- `$config['csrf_protection'] = TRUE` with token regeneration; exclude only verified webhook routes (`csrf_exclude_uris`) and verify their signatures instead.
- `$config['sess_regenerate_destroy']`, `sess_match_ip` where viable; cookies `secure`, `httponly`, `samesite`.
- `$this->input->post('x', TRUE)` XSS filtering is not output encoding: still `html_escape()` in views.
- Uploads via the Upload library with `allowed_types`, `max_size`, `encrypt_name = TRUE`, stored outside `FCPATH`; check MIME by content.
- `ENVIRONMENT` = `production` on live servers (hides errors); `display_errors` off; `log_threshold` without PII.
- Keys and credentials in environment or `env_keys.php` outside git; never `config.php` committed with real values.
- CI3 is legacy (last release 3.1.13, security fixes only): keep PHP on a supported version, track known CVEs, and limit exposure (WAF, admin paths restricted).

## Next.js / Node
- Server Actions and Route Handlers are public endpoints: authenticate and authorize inside each one; validate input with a schema (zod).
- Never expose secrets through `NEXT_PUBLIC_*`; server-only modules marked `import "server-only"`.
- `dangerouslySetInnerHTML` only with sanitized HTML (DOMPurify); CSP with nonces for inline scripts.
- Proxy (called middleware before Next.js 16) is not an authorization layer by itself; re-check in the handler.
- Cookies: `httpOnly`, `secure`, `sameSite`; CSRF protection for cookie-auth mutations outside Server Actions.
- Prisma/Drizzle raw queries via tagged templates only (`$queryRaw\`...\``), never `$queryRawUnsafe` with input.
- Image/remote patterns allow-listed; `fetch` to user-supplied URLs goes through an SSRF allow-list.

## Odoo
Full procedures, per version: skill `odoo`.
- `sudo()` skips access rights and record rules (and can cross companies): document why, check the caller first, never return sudo'ed records.
- Controllers default to `auth='user'`; `public`/`none` need explicit validation; CSRF protects `type='http'` POSTs but not JSON-RPC routes.
- Parameterised queries through the ORM or the `SQL` wrapper only; domains built with `Domain`, never from concatenated input.
- Access for every new model: `ir.model.access.csv` plus record rules up to 19, `ir.access` in 20, with multi-company rules; `groups=` on sensitive fields.

## Flutter / mobile
- No secrets or vendor API keys in the app bundle; the backend proxies privileged calls.
- Tokens in `flutter_secure_storage` (Keychain/Keystore), never SharedPreferences.
- TLS only; consider certificate pinning for lending/KYC flows; reject cleartext (`usesCleartextTraffic=false`).
- Obfuscate release builds (`--obfuscate --split-debug-info=build/symbols`, keeping the symbols for crash reports), disable debug logging of PII, guard screenshots on sensitive screens (FLAG_SECURE).
- Server-side validation remains the authority; the app is untrusted.
- Requirements and tests: OWASP MASVS v2.1.0 and MASTG v2.0.0 (see [standards.md](standards.md)).

## Linux servers (VPS / EC2)
- SSH keys only, `PermitRootLogin no`, `PasswordAuthentication no`, non-default admin user with sudo; fail2ban.
- Firewall: allow 80/443 publicly; 22 restricted by IP where possible; databases, Redis, Supervisor and admin ports bound to localhost or a private network.
- Unattended security updates; TLS via Let's Encrypt with auto-renew; HSTS.
- App processes run as unprivileged users; file permissions least-privilege; no world-writable web roots.
- Backups encrypted and off-site; restore tested; logs kept at least 180 days within India for Indian clients (CERT-In) and clocks synced to NIC/NPL NTP servers.
- Baseline: CIS Benchmark Level 1 for the OS and each service (Ubuntu 24.04 v2.0.0, NGINX v3.1.0, Docker v1.9.0, MySQL 8.4 v1.1.0, MariaDB 10.11 v1.0.0); AWS accounts: CIS AWS Foundations v7.1.0. Apply with care on live servers: some items break apps, so test on UAT first.
- After compromise: rotate every credential, rebuild from a known-good state rather than trusting cleanup, review cron, authorized_keys, systemd units and Server Scripts for persistence.
