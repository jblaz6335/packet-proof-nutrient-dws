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
- 78 automated tests with 98.09% branch-aware coverage.

## Submission checklist

- [x] Product source and MIT license
- [x] Meaningful Nutrient DWS integration code
- [x] Synthetic PDF fixtures
- [x] Deterministic local demo
- [x] Security and human-authority boundary
- [x] Automated verification suite
- [ ] Execute the live Nutrient flow with an authorized API key and retain sanitized proof
- [ ] Publish a public repository or judge-accessible shared link
- [ ] Record and upload the 2–4 minute demonstration video
- [ ] Create the Devpost entry and paste the required one-line DWS statement
- [ ] Submit before September 3, 2026 at 10:00 AM PDT

Official competition: <https://api-cloud-ai-hackathon-2026.devpost.com/>

Official DWS Processor guide: <https://www.nutrient.io/guides/dws-processor/developer-guides/>
