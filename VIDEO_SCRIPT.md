# Packet Proof — 2:40 demo script

## 0:00–0:20 — Hook

Show the report hero and say:

> A shipment packet can look complete and still disagree on the facts that determine release. Packet Proof catches those discrepancies before they become an expensive downstream surprise.

## 0:20–0:45 — The inputs

Show the commercial invoice, packing list, and certificate of origin. Point out that all three are fictional hackathon fixtures. Briefly show 24 units on the invoice and 22 on the packing list without resolving the result yet.

## 0:45–1:15 — Nutrient DWS

Show `packet_proof/provider.py` and the `/build` request. Say:

> Nutrient DWS performs the core document operation. It extracts JSON content—including key-value pairs and tables—from each PDF. Packet Proof accepts that structured evidence and fails closed if the provider response is malformed.

Do not imply that the replay command is a live API call. If authorized live proof has been completed, show its sanitized terminal result separately and label it `live`.

## 1:15–1:50 — Deterministic reconciliation

Run:

```powershell
packet-proof demo --pdf-dir output/pdf --fixture-dir fixtures/extractions --output-dir artifacts
```

Show the JSON summary: three documents, one finding, `human_review_required`, and `auto_released: false`. Explain the checks for packet identity, supplier, SKU, quantity, origin, invoice arithmetic, and extraction confidence.

## 1:50–2:20 — Exception desk

Open `artifacts/packet-report.html`. Show the 24-versus-22 blocking mismatch, the source hashes, and the stable audit hash. Emphasize that the ledger is replayable and each finding is tied to source evidence.

## 2:20–2:40 — Human boundary and close

Show the agent-work/human-authority split and say:

> Packet Proof does not auto-release, sign, amend, transmit, or make a customs decision. It removes repetitive comparison work while keeping the consequential decision with a person.

Close with the exact sponsor line:

> Nutrient DWS extracted structured JSON content from each source PDF; Packet Proof reconciled those extracted fields deterministically and reserved the release decision for a human.
