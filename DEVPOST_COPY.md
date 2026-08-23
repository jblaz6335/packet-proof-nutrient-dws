# Packet Proof — Devpost submission copy

## Project name

Packet Proof

## Tagline

An auditable exception desk that uses Nutrient DWS to extract trade documents, catches cross-document mismatches deterministically, and keeps release authority with a human.

## Built with

Python, Nutrient DWS Processor API, HTML, CSS, pytest

## Inspiration

A shipment packet can look complete while its commercial invoice, packing list, and certificate of origin disagree on facts that determine release. Manual comparison is repetitive, errors surface late, and opaque automation is a poor fit for a compliance-sensitive decision.

## What it does

Packet Proof turns three trade-document PDFs into a deterministic, evidence-linked exception ledger. It normalizes extracted fields, hashes every source, checks packet identity, supplier, SKU, quantity, origin, invoice arithmetic, and confidence, then produces both machine-readable JSON and a human review desk. The included fictional scenario catches a blocking 24-versus-22 quantity mismatch and refuses to auto-release the packet.

## How we built it

The live integration sends each PDF to Nutrient DWS Processor's official `/build` endpoint and requests structured JSON content, including plain text, structured text, key-value pairs, and tables. Packet Proof validates that response, normalizes the evidence, applies deterministic reconciliation rules, and renders a replayable report with page references, SHA-256 source hashes, and a stable audit hash.

The public repository also includes a clearly labeled network-free replay fixture so judges can reproduce the complete reconciliation and UI without credentials. Replay output is synthetic and is not presented as a live API response.

I also completed an authorized live run against all three fictional PDFs. Sanitized DWS responses are retained in the public repository and rebuild the same human-review desk without exposing an API key.

**Required sponsor statement:** Nutrient DWS extracted structured JSON content from each source PDF; Packet Proof reconciled those extracted fields deterministically and reserved the release decision for a human.

## Challenges we ran into

Document automation becomes dangerous when extraction uncertainty is silently treated as truth. We designed the pipeline to fail closed on malformed provider responses, preserve source evidence, surface low-confidence fields for review, and separate machine preparation from human release authority. We also made the audit output stable and reproducible across runs.

## Accomplishments that we're proud of

- A focused sponsor use case with meaningful Nutrient DWS integration.
- A blocking mismatch that is traceable to exact document evidence.
- Deterministic reconciliation rather than an unreviewable model verdict.
- Human-in-the-loop release boundaries built into the product behavior.
- An authorized three-document live DWS run with sanitized, replayable response evidence.
- 80 automated tests and 95.48% branch-aware coverage.
- Fictional fixtures, replay instructions, security documentation, and an MIT-licensed public repository.

## What we learned

Extraction is only the first half of trustworthy document automation. The useful product is the boundary around it: validation, evidence preservation, deterministic rules, confidence handling, auditability, and a clear point where a person must decide.

## What's next

Next steps are configurable customer rule packs, reviewer annotations, exception assignment, ERP/TMS connectors, signed review events, and additional document families. The same architecture can support purchase-order packets, bills of lading, inspection certificates, and regulated onboarding documents.

## Links

- Source: https://github.com/jblaz6335/packet-proof-nutrient-dws
- Blaz Algo Systems: https://blazalgosystems.netlify.app/
- Video: add the public or unlisted URL after upload

## Submission accuracy note

The rendered 2:57 demo uses the repository's labeled synthetic replay path; it is not a recording of the API call. The separate `artifacts/live/` evidence comes from the authorized DWS run against the same three fictional PDFs.
