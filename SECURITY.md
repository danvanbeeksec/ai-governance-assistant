# Security

## Scope

This repository is a synthetic governance demonstration, not a production authorization, assessment, evidence, legal-advice, or recordkeeping system. Do not submit personal, confidential, employer, client, regulated, security-sensitive, or other nonpublic information.

The local stdio MCP server and optional web demonstration intentionally provide no authentication, persistence, database, or telemetry. Bind the web demonstration only to interfaces and networks you intend to expose.

The packaged Claude skill makes no network calls and writes no assessment data, inventory records, or history. It runs inside the selected Claude surface, so conversation and code-execution retention remain subject to that surface's settings and terms. Do not treat the absence of application-level persistence as a guarantee that the host retains nothing.

The self-contained Microsoft 365 kit uses Copilot Studio conversation variables, an embedded knowledge file, and deterministic Power Fx formulas. It includes no assessment-record connector or inventory workflow. Microsoft 365 and Power Platform conversation, audit, diagnostic, analytics, eDiscovery, and retention behavior still follows the installing tenant's configuration. Review those settings before handling anything beyond fictional or synthetic information.

The Streamable HTTP server fails closed unless `AI_GOVERNANCE_API_KEY` is configured and requires that value in the `x-api-key` header. This shared-secret mechanism is an initial interoperability control. Public deployment still requires an independent security review, secret rotation, TLS termination, network restrictions, abuse controls, logging decisions, and privacy analysis. A production deployment should consider user-specific identity and authorization instead of a shared key.

## Reporting a vulnerability

Do not include exploit details or sensitive information in a public issue. Use GitHub private vulnerability reporting when available. Otherwise, contact the repository owner privately through GitHub before public disclosure.

Include the affected release or commit, reproducible steps using synthetic information, likely impact, and any suggested mitigation. Do not test against systems, accounts, or data you do not own or have explicit permission to assess.
