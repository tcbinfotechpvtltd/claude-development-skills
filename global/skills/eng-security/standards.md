# Which security standard governs which work

Editions were confirmed on the official sites on 2026-11-04 (register with URLs: `docs/SOURCES.md` in the eng-os repo). Apply the latest *final* edition; drafts are on the watch list, not applied. There is no single "best" standard: each one below is the recognised reference for its area, so combine them by what the work touches.

## Pick by what you are building or reviewing
| Work | Governing standard (edition) | How to use it |
|---|---|---|
| Web app, portal, admin back office | OWASP ASVS 5.0.0; OWASP Top 10:2025 as the review headings | ASVS L2 as the baseline; L3 for money movement, KYC/PII stores and admin back offices. ASVS items become acceptance criteria and audit pass/fail checks |
| API (mobile backend, NBFC/partner, webhooks) | OWASP API Security Top 10 2023 + ASVS V4 API, V8 Authorization, V9 Tokens, V10 OAuth/OIDC | object-level and property-level authorization on every call, resource limits, treat third-party API responses as untrusted |
| Mobile app (Flutter) | OWASP MASVS v2.1.0 (requirements), MASTG v2.0.0 (tests), Mobile Top 10 2024 | storage, crypto, auth, network, platform, code quality, resilience, privacy |
| LLM features, AI agents, MCP tools | OWASP Top 10 for LLM Applications 2026, Top 10 for Agentic Applications 2026, NIST SP 800-218A | treat model output and retrieved content as untrusted input; least-privilege tools; human approval for consequential actions; no secrets in prompts; log tool calls |
| Login, MFA, passwords, sessions | NIST SP 800-63B-4 + ASVS V6/V7 | rules in the eng-security skill (A07) |
| Team or client secure SDLC | NIST SSDF SP 800-218 v1.1 (Prepare the Organization, Protect the Software, Produce Well-Secured Software, Respond to Vulnerabilities); OWASP SAMM v2.0 to assess maturity | what enterprise and regulated clients' vendor due diligence asks for |
| Build and supply chain | SLSA v1.2 (Build L2: signed provenance from a hosted CI; L3 when a client requires), OpenSSF Scorecard checks, SBOM in CycloneDX 1.7 (or SPDX 3.0.1), CERT-In SBOM/QBOM/CBOM/AIBOM/HBOM guidelines v2.0 for Indian regulated clients | lockfiles, pinned CI actions, least-privilege CI tokens, branch protection, signed releases, dependency update tool |
| Code weaknesses in review and SAST | CWE Top 25 (2025): XSS, SQL injection, CSRF, missing authorization and out-of-bounds write lead it | tag audit findings with CWE IDs |
| Servers, containers, cloud accounts | CIS Benchmarks Level 1 (versions in stacks.md); CIS Controls v8.1 Implementation Group 1 for a small organisation | test hardening on UAT before production |
| Threat modelling and detection | STRIDE per change (skill section 1); MITRE ATT&CK v20.0 to map detections and incidents | |
| Access architecture | NIST SP 800-207 / 800-207A zero trust | authenticate and authorize every request; no trust from network location; per-service identities |
| Card payments | PCI DSS v4.0.1 (future-dated requirements in force since 2025-03-31) | never let card numbers touch our servers. A fully hosted gateway page or redirect keeps a merchant in SAQ A; an embedded payment iframe also needs script-integrity controls (requirements 6.4.3 and 11.6.1) or the gateway's written confirmation; a payment form built by our JavaScript can mean SAQ A-EP. The client confirms scope with its acquirer |
| Organisation programme (client asks for ISO 27001, SOC 2, "NIST") | NIST CSF 2.0 (Govern, Identify, Protect, Detect, Respond, Recover); ISO/IEC 27001:2022 + Amd 1:2024 with 27002:2022 controls; NIST SP 800-53 Rev 5.2.0 as the detailed control catalogue | map what the software provides to these controls; never claim the client is compliant |
| Product security posture | CISA Secure by Design principles (take ownership of customer security outcomes, radical transparency, lead from the top) | secure defaults, MFA available and on for admins, no default passwords, remove whole vulnerability classes, publish a vulnerability disclosure contact |

## Indian obligations that change engineering
- **CERT-In Directions (28 Apr 2022)**: report a cyber incident to CERT-In within 6 hours of noticing it; keep ICT logs for a rolling 180 days within India; sync clocks to NIC/NPL NTP servers (or servers traceable to them); designate a point of contact. The client (data owner) reports: tell them immediately, with facts.
- **CERT-In Comprehensive Cyber Security Audit Policy Guidelines (25 Jul 2025)**: what a CERT-In-empanelled audit of the client will check; build evidence (logs, access reviews, patch records) in advance.
- **DPDP Rules 2025** (core duties from 13 May 2027): reasonable security safeguards (encryption, masking or tokenisation, access control, logging, backups, processor contracts); personal-data processing logs kept at least 1 year; breach intimation to the Data Protection Board and affected users without delay, detailed report within 72 hours.
- **RBI, for NBFC clients**: NBFC Cybersecurity, Technology: Risk, Resilience and Assurance Framework Directions 2026 (31 Jul 2026) and NBFC Managing Risks in Outsourcing Directions 2025 (28 Nov 2025). Lending specifics: skill `fintech-lending`.
- When several clocks apply to one incident (CERT-In 6 hours, DPDP Board, RBI), the shortest one drives the response plan.

## Post-quantum readiness (NIST IR 8547, final 27 Oct 2026)
RSA, ECDSA, EdDSA, DH and ECDH are deprecated after 2030 and disallowed after 2035. Keep algorithms configurable and keys and certificates inventoried. ML-KEM (FIPS 203), ML-DSA (FIPS 204) and SLH-DSA (FIPS 205) are the standards; use hybrid TLS where the platform supports it for data that must stay confidential beyond 2030 (KYC archives, bureau data). Never hand-roll cryptography.

## Watch list (not yet final; check at each eng-os review)
NIST SP 800-218 Rev. 1 (SSDF v1.2, draft of Dec 2025); OWASP WSTG 5.0, ASVS 5.0.1 and the Proactive Controls successor; SPDX 3.1 (release candidate); FIPS 206 (FN-DSA) and the HQC standard; CIS Ubuntu 26.04 benchmark (when servers move to 26.04); the 2026 PCI DSS revision consultation.
