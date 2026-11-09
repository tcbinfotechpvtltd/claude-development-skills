# Sources of the engineering standards

Every external standard that eng-os skills and rules cite, with the edition in use and when it was last confirmed on the official site.

**What "latest" means here**: the newest *final* edition published on the official page on the checked date. Drafts and release candidates are listed in the notes but not adopted. Standards keep moving, so `eng-os verify` warns when a row is older than 120 days, and `/eng-os-review` re-checks every row (section 3 of that skill).

**What is not from a standard**: stack pitfalls (Frappe, CI3, Next.js, Odoo, Flutter, servers), the lending engineering defaults and the severity rubric come from your projects, incidents and audits (memory files, 700+ session transcripts). They are engineering judgement, checked against the standards below where one exists.

## Releases, branches and code review
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| Semantic Versioning | 2.0.0 | not shown | eng-ship/releases.md | https://semver.org/ | 2026-11-04 |
| Keep a Changelog | 1.1.0 | 2019-02-15 | releases.md, templates/release/CHANGELOG.md | https://keepachangelog.com/en/1.1.0/ | 2026-11-04 |
| Conventional Commits | 1.0.0 | not shown | releases.md | https://www.conventionalcommits.org/en/v1.0.0/ | 2026-11-04 |
| GitHub automatically generated release notes | live docs | not shown | releases.md, templates/release/release.yml | https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes | 2026-11-04 |
| GitHub pull request templates | live docs | not shown | releases.md, templates/release/pull_request_template.md | https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository | 2026-11-04 |
| Trunk-based development: short-lived branches | live site | not shown | releases.md | https://trunkbaseddevelopment.com/short-lived-feature-branches/ | 2026-11-04 |
| Google engineering practices: code review | live site | not shown | eng-review, releases.md | https://google.github.io/eng-practices/ | 2026-11-04 |

## Architecture and design
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| C4 model | live site | not shown | eng-design | https://c4model.com/ | 2026-11-04 |
| Architecture Decision Records (Nygard, MADR, Y-statement) | MADR 4.0.0 | templates page updated 2026-11-02 | eng-design | https://adr.github.io/adr-templates/ | 2026-11-04 |
| The Twelve-Factor App | live site | last updated 2017 | eng-design, eng-ship | https://12factor.net/ | 2026-11-04 |
| AWS Well-Architected Framework | 6 pillars | not shown | eng-design | https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html | 2026-11-04 |
| obra/superpowers (agent workflow skills, MIT) | v7.0.2 | 2026-11-03 | eng-design/implementation-plans.md; red-flags tables in eng-review, eng-testing, eng-ship; review feedback in eng-review; subagent model choice in CLAUDE.md section 8; pressure tests in eng-os-review. Ideas adapted in our own words; not installed. | https://github.com/obra/superpowers | 2026-11-09 |

## Testing
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| The Practical Test Pyramid (Ham Vocke, martinfowler.com) | article | 2018-02-26 | eng-testing | https://martinfowler.com/articles/practical-test-pyramid.html | 2026-11-04 |
| OWASP Web Security Testing Guide | v4.2 (stable; 5.0 in progress, not released) | year not shown | eng-testing, eng-security | https://owasp.org/www-project-web-security-testing-guide/ | 2026-11-04 |

## Delivery, operations and reliability
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| DORA software delivery metrics | five metrics (since the 2024 report); latest report 2025 | not shown | eng-ship | https://dora.dev/guides/dora-metrics/ | 2026-11-04 |
| Google SRE book and workbook (SLOs, error budgets, postmortems) | online editions | not shown | eng-ship | https://sre.google/sre-book/service-level-objectives/ | 2026-11-04 |

## Secure development and supply chain
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| NIST SP 800-218 Secure Software Development Framework | v1.1 final (Rev. 1 / v1.2 is an initial public draft of 2025-12-17, not adopted) | 2022-02-03 | eng-security/standards.md | https://csrc.nist.gov/projects/ssdf/publications | 2026-11-04 |
| NIST SP 800-218A SSDF profile for generative AI | final | 2024-07-26 | eng-security/standards.md | https://csrc.nist.gov/pubs/sp/800/218/a/final | 2026-11-04 |
| SLSA (supply-chain levels) | v1.2 (Build and Source tracks) | not shown | eng-security/standards.md | https://slsa.dev/spec/v1.2/ | 2026-11-04 |
| OpenSSF Scorecard checks | live (20 checks) | not shown | eng-security/standards.md | https://github.com/ossf/scorecard/blob/main/docs/checks.md | 2026-11-04 |
| CycloneDX SBOM | 1.7 | 2025-10-21 | eng-security/standards.md, eng-ship | https://cyclonedx.org/specification/overview/ | 2026-11-04 |
| SPDX | 3.0.1 (3.1 is a release candidate) | 2024-12-17 | eng-security/standards.md | https://github.com/spdx/spdx-spec/releases | 2026-11-04 |
| CERT-In Technical Guidelines on SBOM, QBOM & CBOM, AIBOM and HBOM | v2.0 | 2025-07-09 | eng-security/standards.md | https://www.cert-in.org.in/ | 2026-11-04 |
| OWASP ASVS | 5.0.0 | 2025-05-30 | eng-security, eng-testing | https://asvs.owasp.org/ | 2026-11-04 |

## Application security (OWASP, MITRE, CISA)
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| OWASP Top 10 (web) | 2025 final, the latest: no newer edition or draft on the official site | announced 2025 (exact date not stated) | eng-security | https://owasp.org/www-project-top-ten/ | 2026-11-04 |
| OWASP API Security Top 10 | 2023 | not shown | eng-security/standards.md | https://owasp.org/API-Security/ | 2026-11-04 |
| OWASP Mobile Top 10 | 2024 final | not shown | eng-security/standards.md | https://owasp.org/www-project-mobile-top-10/ | 2026-11-04 |
| OWASP MASVS (mobile verification standard) | v2.1.0 | 2024-01-18 | eng-security/standards.md | https://mas.owasp.org/MASVS/ | 2026-11-04 |
| OWASP MASTG (mobile testing guide) | v2.0.0 | 2026-06-30 | eng-security/standards.md | https://mas.owasp.org/MASTG/ | 2026-11-04 |
| OWASP Top 10 for LLM Applications | 2026 | 2026-08-03 | eng-security/standards.md | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | 2026-11-04 |
| OWASP Top 10 for Agentic Applications | 2026 edition | 2025-12-09 | eng-security/standards.md | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | 2026-11-04 |
| OWASP Proactive Controls | 2024 (v4.0.0; a successor is a work in progress) | 2024-10-20 | eng-security/standards.md | https://top10proactive.owasp.org/ | 2026-11-04 |
| OWASP SAMM (maturity model) | v2.0 | 2020-02-03 | eng-security/standards.md | https://owaspsamm.org/model/ | 2026-11-04 |
| OWASP Cheat Sheet Series | live (137 sheets) | continuously updated | eng-security/standards.md | https://cheatsheetseries.owasp.org/ | 2026-11-04 |
| CWE Top 25 Most Dangerous Software Weaknesses | 2025 | 2025-12-11 | eng-security/standards.md | https://cwe.mitre.org/top25/ | 2026-11-04 |
| MITRE ATT&CK | v20.0 | 2026-10-13 | eng-security/standards.md | https://attack.mitre.org/resources/versions/ | 2026-11-04 |
| CISA Secure by Design (principles, pledge, Secure by Demand) | principles 2023-10; pledge 2024-05-08; Secure by Demand 2024-08-06 | see edition | eng-security/standards.md | https://www.cisa.gov/securebydesign | 2026-11-04 |

## Security frameworks and baselines (NIST, CIS, PCI, ISO, CERT-In)
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| NIST Cybersecurity Framework | CSF 2.0 | 2024-02-26 | eng-security/standards.md | https://www.nist.gov/cyberframework | 2026-11-04 |
| NIST SP 800-63-4 Digital Identity Guidelines (incl. 800-63B-4) | 800-63-4 final (supersedes -3) | 2025-07-31 | eng-security | https://csrc.nist.gov/pubs/sp/800/63/4/final | 2026-11-04 |
| NIST SP 800-53 security and privacy controls | Rev 5, release 5.2.0 | 2025-08-27 | eng-security/standards.md | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final | 2026-11-04 |
| NIST SP 800-207 Zero Trust Architecture (+ 800-207A) | final | 2020-08-11 (207A 2023-09-13) | eng-security/standards.md | https://csrc.nist.gov/pubs/sp/800/207/final | 2026-11-04 |
| NIST post-quantum standards FIPS 203/204/205 | final | 2024-08-13 | eng-security/standards.md | https://csrc.nist.gov/publications/fips | 2026-11-04 |
| NIST IR 8547 transition to post-quantum cryptography | final | 2026-10-27 | eng-security | https://csrc.nist.gov/News/2026/transition-to-pqc-standards-nist-ir-8547 | 2026-11-04 |
| CIS Critical Security Controls | v8.1 | 2024-06-25 | eng-security/standards.md | https://www.cisecurity.org/controls | 2026-11-04 |
| CIS Benchmarks (Ubuntu 24.04 v2.0.0, AWS Foundations v7.1.0, NGINX v3.1.0, Docker v1.9.0, MySQL 8.4 v1.1.0, MariaDB 10.11 v1.0.0) | as listed | 2026-05 to 2026-10 | eng-security/stacks.md, standards.md | https://www.cisecurity.org/cis-benchmarks | 2026-11-04 |
| PCI DSS | v4.0.1 (future-dated requirements in force since 2025-03-31) | 2024-06-11 | eng-security/standards.md, fintech-lending | https://blog.pcisecuritystandards.org/just-published-pci-dss-v4-0-1 | 2026-11-04 |
| ISO/IEC 27001 / 27002 | 27001:2022 + Amd 1:2024; 27002:2022 | 2022-10-25 | eng-security/standards.md | https://committee.iso.org/isoiec-27001-information-security.html | 2026-11-04 |
| CERT-In Directions under section 70B(6) of the IT Act | No. 20(3)/2022-CERT-In | 2022-04-28 | eng-security, eng-ship | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf | 2026-11-04 |
| CERT-In Comprehensive Cyber Security Audit Policy Guidelines | CISG-2025-02 v1.0 | 2025-07-25 | eng-security/standards.md | https://www.cert-in.org.in/s2cMainServlet?pageid=GUIDLNVIEW01 | 2026-11-04 |

## Indian regulation (lending, data protection, NBFC technology)
Primary RBI pages were read for the Digital Lending Directions; DPDP Rules content comes from the PIB factsheet and law-firm summaries because the MeitY and gazette pages refused automated access. Confirm with the client's compliance owner before a rule decides behaviour.

| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| RBI (Digital Lending) Directions, 2025 (RBI/2025-26/36) | as issued; para 6 from 2025-11-01, para 17 from 2025-06-15 | 2025-05-08 | fintech-lending | https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12848 | 2026-11-04 |
| RBI NBFC (Credit Facilities) Directions, 2025, Chapter III (digital lending restated after the Nov 2025 consolidation) | RBI/DOR/2025-26/347 | 2025-11-28 | fintech-lending | https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12957 | 2026-11-04 |
| RBI NBFC Cybersecurity, Technology: Risk, Resilience and Assurance Framework Directions, 2026 | RBI/DoS/2026-27/461 | 2026-07-31 | fintech-lending, eng-security/standards.md | https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=13592 | 2026-11-04 |
| RBI NBFC Managing Risks in Outsourcing Directions, 2025 | RBI/DOR/2025-26/363 | 2025-11-28 | fintech-lending, eng-security/standards.md | https://rbi.org.in/scripts/BS_ViewMasDirections.aspx?id=12941 | 2026-11-04 |
| Digital Personal Data Protection Rules, 2025 (G.S.R. 846(E)) | as notified; Rule 4 from 2026-11-13, core rules from 2027-05-13 | 2025-11-13 | fintech-lending, eng-security/standards.md | https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf | 2026-11-04 |

## Delivery and project management
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| The Scrum Guide | 2020 (still current) | 2020-11 | eng-delivery | https://scrumguides.org/scrum-guide.html | 2026-11-04 |
| The Kanban Guide | v2025.5 | 2025-05 | eng-delivery | https://kanbanguides.org/english/ | 2026-11-04 |
| PMI PMBOK Guide | 8th edition (domains per PMI's announcement; PMI pages refuse automated access) | 2025-11 | eng-delivery | https://www.pmi.org/standards/pmbok | 2026-11-04 |
| PRINCE2 | 7th edition | 2023-09 | eng-delivery | https://www.peoplecert.org/browse-certifications/project-programme-and-portfolio-management/PRINCE2-2 | 2026-11-04 |
| Manifesto for Agile Software Development | original, 12 principles | 2001 | eng-delivery | https://agilemanifesto.org/principles.html | 2026-11-04 |
| Three-point (PERT) estimation; cone of uncertainty | reference articles | not applicable | eng-delivery | https://en.wikipedia.org/wiki/Three-point_estimation | 2026-11-04 |

## Coding standards
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| PEP 8 Style Guide for Python Code | living document | last modified 2025-04-04 | eng-review/coding-standards.md | https://peps.python.org/pep-0008/ | 2026-11-04 |
| Ruff (Python linter and formatter) | 0.17 | 2026-10-26 | coding-standards.md | https://docs.astral.sh/ruff/ | 2026-11-04 |
| PHP-FIG PER Coding Style | 3.1 (extends and replaces PSR-12) | not shown | coding-standards.md, custom-apps/php-ci3.md | https://www.php-fig.org/per/coding-style/ | 2026-11-04 |
| PHP_CodeSniffer | 4.0.4 | 2026-08-06 | coding-standards.md | https://github.com/PHPCSStandards/PHP_CodeSniffer/releases | 2026-11-04 |
| ESLint | 10 (flat config) | 2026-10-30 (10.14) | coding-standards.md | https://eslint.org/docs/latest/use/configure/configuration-files | 2026-11-04 |
| typescript-eslint | 8.72 | 2026-10-26 | coding-standards.md | https://typescript-eslint.io/users/configs | 2026-11-04 |
| Prettier | 3.9 | 2026-06-27 | coding-standards.md | https://prettier.io/blog/ | 2026-11-04 |
| Effective Dart; lints / flutter_lints | lints 6.1, flutter_lints 6.0 | not shown | coding-standards.md | https://dart.dev/effective-dart | 2026-11-04 |
| Frappe repo lint setup (ruff, ESLint, Prettier, commitlint) | develop branch | not applicable | coding-standards.md | https://github.com/frappe/frappe/blob/develop/.pre-commit-config.yaml | 2026-11-04 |

## GitHub
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| GitHub rulesets and protected branches | live docs | not shown | eng-ship/github.md | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | 2026-11-04 |
| GitHub code owners | live docs | not shown | github.md | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners | 2026-11-04 |
| Dependabot (alerts, security and version updates) | live docs | not shown | github.md | https://docs.github.com/en/code-security/dependabot | 2026-11-04 |
| Secret scanning and push protection | live docs | not shown | github.md | https://docs.github.com/en/code-security/secret-scanning | 2026-11-04 |
| GitHub Actions secure use (hardening) and OIDC | live docs | not shown | github.md, rule ci-deploy | https://docs.github.com/en/actions/reference/security/secure-use | 2026-11-04 |
| Artifact attestations | live docs | not shown | github.md | https://docs.github.com/en/actions/concepts/security/artifact-attestations | 2026-11-04 |
| GitHub flow | live docs | not shown | github.md | https://docs.github.com/en/get-started/using-github/github-flow | 2026-11-04 |
| Trivy supply-chain compromise advisory | GHSA-69fq-xp46-6x23 / CVE-2026-33634 | 2026-03-21 | github.md, eng-testing/tooling.md | https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23 | 2026-11-04 |

## Test tooling and quality targets
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| WCAG | 2.2 Recommendation (3.0 is a working draft) | 2023-10-05, updated 2024-12-12 | eng-testing/tooling.md | https://www.w3.org/TR/WCAG22/ | 2026-11-04 |
| Core Web Vitals (LCP, INP, CLS) | current thresholds | not shown | tooling.md, custom-apps/nextjs.md | https://web.dev/articles/vitals | 2026-11-04 |
| Playwright | 1.64 | 2026-10-14 | tooling.md | https://playwright.dev/docs/release-notes | 2026-11-04 |
| Vitest / Jest | Vitest 5.1, Jest 30.5 | 2026-11-02 / 2026-09-18 | tooling.md | https://vitest.dev/guide/ | 2026-11-04 |
| pytest | 9.2 | 2026-10-27 | tooling.md | https://pypi.org/project/pytest/ | 2026-11-04 |
| PHPUnit | 13 (PHP 8.4+); 12 (PHP 8.3+) | 2026-02-06 | tooling.md | https://phpunit.de/supported-versions.html | 2026-11-04 |
| Flutter testing (unit, widget, integration_test, goldens) | live docs | not shown | tooling.md, custom-apps/flutter.md | https://docs.flutter.dev/testing/overview | 2026-11-04 |
| Grafana k6 | 2.3 | 2026-09-21 | tooling.md | https://grafana.com/docs/k6/latest/ | 2026-11-04 |
| Pact contract testing | specification v4 (v3 widely supported) | not shown | tooling.md | https://docs.pact.io/ | 2026-11-04 |
| ZAP by Checkmarx / Semgrep CE / gitleaks / Trivy | 2.17 / 1.183 / 8.30 / 0.76 | 2025-12-15 to 2026-10-29 | tooling.md | https://www.zaproxy.org/download/ | 2026-11-04 |

## Custom-app runtimes and frameworks
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| Next.js (and upgrade guides, data-security guide) | 16.4 | 2026-10-06 | custom-apps/nextjs.md | https://nextjs.org/blog/next-16-4 | 2026-11-04 |
| React | 19.3 | 2026-09-09 | custom-apps | https://react.dev/versions | 2026-11-04 |
| Node.js release schedule | 26 Active LTS; 24, 22 maintenance | 2026-10-28 | custom-apps | https://github.com/nodejs/Release/blob/main/schedule.json | 2026-11-04 |
| TypeScript | 7.0 | 2026-06-18 | custom-apps | https://devblogs.microsoft.com/typescript/ | 2026-11-04 |
| Flutter / Dart (and app-architecture guide) | Flutter 3.47, Dart 3.13 | 2026-10-29 | custom-apps/flutter.md | https://docs.flutter.dev/app-architecture/guide | 2026-11-04 |
| PHP supported versions | 8.2–8.5 | not applicable | custom-apps/php-ci3.md | https://www.php.net/supported-versions.php | 2026-11-04 |
| CodeIgniter 3 / CodeIgniter 4 | 3.1.13 (legacy) / 4.7 | 2022-03-03 / 2026-11 | custom-apps/php-ci3.md | https://github.com/bcit-ci/CodeIgniter | 2026-11-04 |
| Python release status | 3.15 latest; 3.11 oldest with security fixes | 2026-10-25 | custom-apps/python.md | https://www.python.org/downloads/ | 2026-11-04 |

## Odoo
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| Odoo supported versions | 20.0 latest (support to 2029-09); 19.0, 18.0 supported; 17.0 out of standard support | 2026-09 | odoo | https://www.odoo.com/documentation/19.0/administration/standard_extended_support.html | 2026-11-04 |
| Odoo coding guidelines | 20.0 | 2026-09 | odoo, eng-review/coding-standards.md | https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html | 2026-11-04 |
| Odoo ORM changelog | 20.0 (covers 17 to 20) | 2026-09 | odoo | https://www.odoo.com/documentation/20.0/developer/reference/backend/orm/changelog.html | 2026-11-04 |
| Odoo security reference and HTTP routes | 20.0 | 2026-09 | odoo, eng-security/stacks.md | https://www.odoo.com/documentation/20.0/developer/reference/backend/security.html | 2026-11-04 |
| Odoo testing and CLI reference | 20.0 | 2026-09 | odoo, eng-testing/tooling.md | https://www.odoo.com/documentation/20.0/developer/reference/backend/testing.html | 2026-11-04 |
| Odoo upgrade scripts, upgrade service, upgrade-util | 20.0 | 2026-09 | odoo | https://www.odoo.com/documentation/20.0/developer/reference/upgrades/upgrade_scripts.html | 2026-11-04 |
| Odoo performance reference | 20.0 | 2026-09 | odoo | https://www.odoo.com/documentation/20.0/developer/reference/backend/performance.html | 2026-11-04 |
| PHP-CS-Fixer rule sets (`@PER-CS`) | 3.95 | 2026-09-22 | eng-review/coding-standards.md | https://github.com/PHP-CS-Fixer/PHP-CS-Fixer/blob/master/doc/ruleSets/index.rst | 2026-11-04 |
| Odoo `neutralize` command and module loading (reinit) | 19.0 source | 2026-08-17 build | odoo | https://github.com/odoo/odoo/blob/19.0/odoo/cli/neutralize.py | 2026-11-04 |

## Browser testing and more test tools
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| Playwright MCP server | 0.0.84 | 2026-10-31 | eng-testing/browser.md | https://github.com/microsoft/playwright-mcp | 2026-11-04 |
| Chrome DevTools MCP server | 1.12.0 | 2026-10-22 | browser.md | https://github.com/ChromeDevTools/chrome-devtools-mcp | 2026-11-04 |
| Playwright visual comparisons (`toHaveScreenshot`) | live docs | not shown | browser.md, test-types.md | https://playwright.dev/docs/test-snapshots | 2026-11-04 |
| axe-core / @axe-core/playwright | 4.14.0 / 4.14.0 | 2026-10-05 / 2026-10-15 | browser.md, tooling.md | https://github.com/dequelabs/axe-core-npm | 2026-11-04 |
| Lighthouse / Lighthouse CI | 13.6.0 / 0.16.0 | 2026-10-27 / 2026-11-02 | browser.md, tooling.md | https://github.com/GoogleChrome/lighthouse-ci | 2026-11-04 |
| Hypothesis / fast-check (property-based testing) | 6.170 / 4.10 | 2026-10-30 / 2026-09-19 | tooling.md, test-types.md | https://pypi.org/project/hypothesis/ | 2026-11-04 |
| Schemathesis (schema-driven API testing) | 4.33.0 | 2026-11-01 | tooling.md, test-types.md | https://pypi.org/project/schemathesis/ | 2026-11-04 |
| Atheris (Python fuzzing) | 3.1.0 | 2026-06-17 | tooling.md | https://github.com/google/atheris | 2026-11-04 |
| Faker / @faker-js/faker | 40.44 / 10.6 | 2026-10-28 / 2026-08-14 | tooling.md | https://pypi.org/project/Faker/ | 2026-11-04 |
| Software Engineering at Google, ch. 11 (test sizes) | online edition | not shown | tooling.md | https://abseil.io/resources/swe-book/html/ch11.html | 2026-11-04 |

## Documentation, delivery tracking and company rollout
| Standard | Edition in use | Published | Used in | URL | Checked |
|---|---|---|---|---|---|
| Diátaxis documentation framework | live site | not shown | eng-docs, templates/docs/user-manual | https://diataxis.fr/ | 2026-11-04 |
| arc42 architecture template | v9.1 (English) | 2026-10-19 | eng-docs, templates/docs/architecture.md | https://arc42.org/overview | 2026-11-04 |
| ISO/IEC/IEEE 29148 requirements engineering | 2018 (2nd ed.; revision under development) | 2018-11-28 | eng-docs, templates/docs/requirements.md | https://www.iso.org/standard/72089.html | 2026-11-04 |
| ISO/IEC/IEEE 29119-3 test documentation | 2021 (2nd ed.) | 2021-10-28 | eng-docs, templates/docs/test-plan.md | https://standards.ieee.org/ieee/29119-3/7499/ | 2026-11-04 |
| Google developer documentation style guide | live | not shown | eng-docs | https://developers.google.com/style/highlights | 2026-11-04 |
| Microsoft Writing Style Guide | live | 2026-10-15 | eng-docs | https://learn.microsoft.com/en-us/style-guide/welcome/ | 2026-11-04 |
| Docusaurus / MkDocs / Material for MkDocs status | 3.10 / 1.6.1 / maintenance mode until 2027-05-05 | 2026-07-10 / 2024-08-30 / 2025-11-11 | eng-docs | https://squidfunk.github.io/mkdocs-material/ | 2026-11-04 |
| Mermaid | 12 | 2026-11-03 | eng-docs | https://mermaid.js.org/ | 2026-11-04 |
| GitHub issue forms | live docs | not shown | templates/github | https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms | 2026-11-04 |
| Claude Code managed and server-managed settings | live docs | not shown | docs/COMPANY-ROLLOUT.md | https://code.claude.com/docs/en/server-managed-settings.md | 2026-11-04 |
| Claude Code plugins and marketplaces | live docs | not shown | docs/COMPANY-ROLLOUT.md | https://code.claude.com/docs/en/plugins/org.md | 2026-11-04 |
| Frappe partner implementation procedure and partner implementation page | live pages | 2026-05-07 | eng-delivery/erp-implementation.md | https://frappe.io/partner-sop/implementation-procedure | 2026-11-04 |
| ERPNext Data Import | live docs | 2026-04-27 | erp-implementation.md | https://docs.frappe.io/erpnext/user/manual/en/data-import | 2026-11-04 |
| Odoo implementation methodology guide | Nov 2020 edition | 2020-11 | erp-implementation.md | https://www.odoo.com/web/content/27370198 | 2026-11-04 |
| Microsoft Dynamics 365 Success by Design and cutover guidance | live docs (5 phases) | 2026-08-04 | erp-implementation.md | https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/success-by-design | 2026-11-04 |
| SAP Activate (phases, fit-to-standard) | as described by SAP LeanIX (SAP pages refuse automated access) | not shown | erp-implementation.md | https://www.leanix.net/en/wiki/ea/sap-activate-explore-phase-activities | 2026-11-04 |
| Claude Code data usage (training on Free/Pro/Max when Model Improvement is on; Team/Enterprise commercial terms) | live docs | not shown | docs/COMPANY-ROLLOUT.md, ENGINEERING-POLICY.md | https://code.claude.com/docs/en/data-usage | 2026-11-04 |
| Anthropic privacy center: model training and retention (5 years on, 30 days off) | live pages | not shown | docs/COMPANY-ROLLOUT.md | https://privacy.claude.com/en/articles/10023580-is-my-data-used-for-model-training | 2026-11-04 |
| Claude Team plan | live page | not shown | docs/COMPANY-ROLLOUT.md | https://support.claude.com/en/articles/9266767-what-is-the-team-plan | 2026-11-04 |
| Claude Code hooks reference (UserPromptSubmit and SessionStart input and additionalContext; 10,000-character limit) | live docs | not shown | hooks prompt_router.py, session_start.py | https://code.claude.com/docs/en/hooks | 2026-11-04 |
| Claude Code skills (invocation, frontmatter) and memory (path-scoped rules) | live docs | not shown | global CLAUDE.md section 6, global/rules | https://code.claude.com/docs/en/skills | 2026-11-04 |
