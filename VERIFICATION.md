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
- Tests: 78 passed
- Branch-aware coverage: 98.09% (project threshold: 90%)
- Dependency consistency: pass
- Demo status: `human_review_required`
- Documents: 3
- Expected findings: 1 (`quantity_mismatch`)
- Automatic release: false
- External calls in demo mode: 0
- Submission video: H.264/AAC, 1920x1080, 2:57, audio mean -20.4 dB

## Scope of proof

The suite covers input validation, required and unique document types, every deterministic comparison branch, invoice arithmetic, confidence thresholds, stable audit hashes, HTML escaping, CLI execution gates, exact mocked Nutrient request construction, provider error handling, fixture hashing, and PDF text/label integrity.

This record does **not** claim a live Nutrient call, video upload, Devpost submission, prize, sale, or revenue. Those require separate external evidence. The repository is public and the submission video has been rendered locally but is not yet uploaded.
