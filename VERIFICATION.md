# Verification record

Verified locally on August 22, 2026 using Python 3.14.5 on Windows.

## Reproduce the evidence

```powershell
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\python.exe -m pytest --cov=packet_proof --cov-report=term-missing
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m packet_proof demo --pdf-dir output/pdf --fixture-dir fixtures/extractions --output-dir artifacts
```

## Latest verified result

- Formatting: pass
- Lint: pass
- Tests: 80 passed
- Branch-aware coverage: 95.48% (project threshold: 90%)
- Dependency consistency: pass
- Demo status: `human_review_required`
- Documents: 3
- Expected findings: 1 (`quantity_mismatch`)
- Automatic release: false
- External calls in demo mode: 0
- Authorized live Nutrient run: pass; 3 fictional PDFs processed at the official `/build` endpoint
- Live result: `human_review_required`, 24-versus-22 quantity mismatch, automatic release false
- Sanitized live evidence: retained under `artifacts/live/`; no API key or authorization header stored
- Submission video: H.264/AAC, 1920x1080, 2:25, 48 kHz mono audio, mean -15.5 dB and peak -1.2 dB
- Narration: locally rendered with the open-source Kokoro ONNX stack; no cloud voice service used

## Scope of proof

The suite covers input validation, required and unique document types, every deterministic comparison branch, invoice arithmetic, confidence thresholds, stable audit hashes, HTML escaping, CLI execution gates, exact mocked Nutrient request construction, provider error handling, fixture hashing, and PDF text/label integrity.

The authorized live Nutrient calls were executed only against the three fictional PDFs. The retained response files can be replayed with `python tools/replay_live_responses.py`. The improved demo upload is verified as unlisted at `https://youtu.be/AgYh_pTIXpI`, and the final Devpost submission is verified at `https://devpost.com/software/packet-proof`. This record does **not** claim a prize, sale, or revenue.
