"""Rebuild the live evidence report from retained fictional DWS responses."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from packet_proof.engine import reconcile_packet
from packet_proof.provider import NutrientProvider
from packet_proof.report import write_report

DOCUMENTS = (
    ("commercial-invoice", "commercial_invoice", "commercial-invoice.pdf"),
    ("packing-list", "packing_list", "packing-list.pdf"),
    ("origin-certificate", "origin_certificate", "origin-certificate.pdf"),
)


def main() -> None:
    output = Path("artifacts/live")
    documents = []
    extraction_summary = []
    for document_id, document_type, filename in DOCUMENTS:
        pdf = Path("output/pdf") / filename
        response = json.loads(
            (output / f"nutrient-{document_id}-response.json").read_text(encoding="utf-8")
        )
        document = NutrientProvider._normalize(
            response,
            document_id,
            document_type,
            hashlib.sha256(pdf.read_bytes()).hexdigest(),
        )
        documents.append(document)
        extraction_summary.append(
            {
                "document_id": document.document_id,
                "document_type": document.document_type,
                "provider": document.provider,
                "sha256": document.sha256,
                "fields": [
                    {
                        "name": field.name,
                        "value": field.value,
                        "confidence": str(field.confidence),
                        "page": field.page,
                    }
                    for field in document.fields
                ],
            }
        )
    result = reconcile_packet(documents)
    (output / "live-extraction-summary.json").write_text(
        json.dumps(extraction_summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    (output / "packet-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_report(result, output / "packet-report.html")
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_mode": result["provider_mode"],
                "document_count": result["document_count"],
                "finding_count": len(result["findings"]),
                "auto_released": result["auto_released"],
                "report": str(output / "packet-report.html"),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
