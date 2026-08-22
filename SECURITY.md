# Security and data boundaries

Packet Proof is a demonstration system, not a customs broker, release authority, or document-of-record service.

## Data handling

- The checked-in PDFs contain only fictional entities, addresses, identifiers, and values.
- Local demo mode makes no network request and uses recorded synthetic extraction fixtures.
- Live mode sends exactly the three selected PDFs to the official Nutrient DWS endpoint only after the CLI's two-part execution gate is satisfied.
- API credentials are read from `NUTRIENT_API_KEY`; they are never accepted as CLI arguments, written to reports, or committed.
- Every source PDF is SHA-256 hashed so a reviewer can tie a finding to an exact input without embedding the document in the audit result.
- Provider failures and malformed extractions fail closed. There is no automatic retry or silent fallback from live extraction to fixtures.

## Human authority

The engine can identify deterministic discrepancies, but `auto_released` is always `false`. A person must review exceptions, obtain corrections, and make any operational or compliance decision.

## Before production use

A production deployment would require authentication, authorization, encryption-at-rest, retention and deletion controls, tenant isolation, audit-log access policy, secrets management, regional processing review, rate limiting, observability, incident response, and legal/compliance review for the relevant trade workflow.

## Reporting vulnerabilities

Do not include credentials, real commercial documents, or personal data in a report. For this hackathon package, document the reproduction against the included synthetic fixtures and identify the affected version.
