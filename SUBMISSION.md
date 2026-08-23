# Packet Proof — submission brief

## One-line product description

Packet Proof uses Nutrient DWS to extract a commercial invoice, packing list, and certificate of origin, then produces a deterministic, evidence-linked exception ledger for human release review.

## The problem

A shipment packet may look complete while disagreeing on a purchase order, supplier, SKU, quantity, origin, or invoice arithmetic. Manual checks are repetitive, late discoveries are expensive, and opaque automation is a poor fit for a compliance-sensitive release decision.

## The solution

Nutrient DWS performs the core document operation: it converts each PDF into structured JSON content with plain text, structured text, key-value pairs, and tables. Packet Proof normalizes those results, hashes the sources, applies deterministic cross-document rules, and renders a replayable exception desk. The demo deliberately catches a 24-versus-22 unit discrepancy.

## Where Nutrient DWS did the work

**Nutrient DWS extracted structured JSON content from each source PDF at the official `/build` endpoint; Packet Proof reconciled those extracted fields deterministically and reserved the release decision for a human.**

## What is demonstrable now

- Three polished, fictional one-page trade-document fixtures.
- A network-free replay mode that produces one expected blocking quantity mismatch.
- An official-origin-only Nutrient adapter with a deliberate two-part live execution gate.
- SHA-256 source ledger, stable audit hash, page evidence, confidence review, and fail-closed validation.
- HTML exception desk plus machine-readable JSON result.
- An authorized live DWS run against all three fictional PDFs, with sanitized response evidence retained for replay.
- 80 automated tests with 95.48% branch-aware coverage.

## Submission checklist

- [x] Product source and MIT license
- [x] Meaningful Nutrient DWS integration code
- [x] Synthetic PDF fixtures
- [x] Deterministic local demo
- [x] Security and human-authority boundary
- [x] Automated verification suite
- [x] Execute the live Nutrient flow with an authorized API key and retain sanitized proof
- [x] Publish a public repository or judge-accessible shared link
- [x] Render the 2–4 minute demonstration video locally (`submission-assets/packet-proof-demo.mp4`, 2:25)
- [ ] Upload the demonstration video and retain the public or unlisted URL
- [x] Create the Devpost draft and set its solo-project name and pitch
- [ ] Complete the Devpost details and paste the required one-line DWS statement
- [ ] Submit before September 3, 2026 at 10:00 AM PDT

Official competition: <https://api-cloud-ai-hackathon-2026.devpost.com/>

Official DWS Processor guide: <https://www.nutrient.io/guides/dws-processor/developer-guides/>
