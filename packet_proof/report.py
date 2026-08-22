from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def write_report(result: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    findings = (
        "".join(
            "<tr>"
            f"<td><span class='badge {html.escape(item['severity'])}'>{html.escape(item['severity'])}</span></td>"
            f"<td>{html.escape(item['code'])}</td><td>{html.escape(item['message'])}</td>"
            "</tr>"
            for item in result["findings"]
        )
        or "<tr><td colspan='3'>No deterministic mismatches found.</td></tr>"
    )
    documents = "".join(
        "<tr>"
        f"<td>{html.escape(item['document_type'].replace('_', ' ').title())}</td>"
        f"<td>{html.escape(item['document_id'])}</td>"
        f"<td><code>{html.escape(item['sha256'][:16])}...</code></td>"
        f"<td>{html.escape(item['provider'])}</td>"
        "</tr>"
        for item in result["documents"]
    )
    payload = html.escape(json.dumps(result, indent=2))
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Packet Proof</title>
<style>
:root{{--navy:#0b1736;--blue:#2667ff;--cream:#f6f2e8;--paper:#fffdf8;--line:#d8d5cb;--red:#ef6b5b;--amber:#f2bb4a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--cream);color:var(--navy);font:16px/1.45 Arial,sans-serif}}
main{{max-width:1160px;margin:auto;padding:54px 36px 74px}}.eyebrow{{font-size:13px;font-weight:800;letter-spacing:.17em;color:var(--blue)}}
h1{{font-size:66px;line-height:.98;margin:14px 0 18px;max-width:900px}}.lede{{font-size:22px;max-width:800px;color:#526078}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:38px 0}}.card,section{{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:22px}}
.card span{{display:block;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:#667089}}.card strong{{font-size:32px}}
section{{margin-top:20px}}h2{{margin:0 0 15px;font-size:25px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:13px 12px;text-align:left;border-bottom:1px solid var(--line)}}
th{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#667089}}.badge{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:11px;font-weight:800;text-transform:uppercase}}.block{{background:#ffd9d3}}.review{{background:#ffe8b1}}
.boundary{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}pre{{background:var(--navy);color:#eef3ff;padding:18px;border-radius:14px;max-height:330px;overflow:auto;white-space:pre-wrap}}
@media(max-width:800px){{h1{{font-size:44px}}.cards,.boundary{{grid-template-columns:1fr}}}}
</style></head><body><main><div class="eyebrow">DEVNETWORK 2026 · NUTRIENT DWS ROUTE · LOCAL SYNTHETIC PROOF</div>
<h1>Catch the mismatch<br>before customs does.</h1><p class="lede">Packet Proof turns extracted trade documents into a deterministic exception desk: every source is hashed, every discrepancy is cited, and nothing is released without a person.</p>
<div class="cards"><div class="card"><span>Documents</span><strong>{result["document_count"]}</strong></div><div class="card"><span>Findings</span><strong>{len(result["findings"])}</strong></div><div class="card"><span>Auto-released</span><strong>No</strong></div><div class="card"><span>Mode</span><strong>{html.escape(result["provider_mode"])}</strong></div></div>
<section><h2>Exception ledger</h2><table><thead><tr><th>Severity</th><th>Code</th><th>Evidence</th></tr></thead><tbody>{findings}</tbody></table></section>
<section><h2>Source ledger</h2><table><thead><tr><th>Type</th><th>ID</th><th>SHA-256</th><th>Extraction</th></tr></thead><tbody>{documents}</tbody></table></section>
<section class="boundary"><div><h2>Agent work</h2><ul><li>Send each PDF to Nutrient DWS extraction.</li><li>Normalize fields with page evidence.</li><li>Recalculate invoice math.</li><li>Cross-check packet identity, SKU, quantity, and origin.</li></ul></div><div><h2>Human authority</h2><ul><li>Review every exception.</li><li>Confirm corrective documents.</li><li>Approve or reject release.</li><li>Own the final compliance decision.</li></ul></div></section>
<section><h2>Replayable result</h2><p>Audit hash: <code>{result["audit_hash"]}</code></p><pre>{payload}</pre></section>
</main></body></html>"""
    output.write_text(document, encoding="utf-8")
