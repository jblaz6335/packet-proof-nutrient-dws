from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any

from .models import ExtractedDocument, ValidationError, decimal_value

REQUIRED_TYPES = {"commercial_invoice", "packing_list", "origin_certificate"}
MIN_CONFIDENCE = Decimal("0.90")


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    evidence: tuple[str, ...]


def _field(document: ExtractedDocument, name: str):
    value = document.values().get(name)
    if value is None:
        raise ValidationError(f"{document.document_type} missing required field {name}")
    return value


def _compare(left, right, code: str, label: str) -> Finding | None:
    if left.value == right.value:
        return None
    return Finding(
        code,
        "block",
        f"{label} mismatch: {left.value} versus {right.value}",
        (f"page {left.page}", f"page {right.page}"),
    )


def reconcile_packet(documents: list[ExtractedDocument]) -> dict[str, Any]:
    by_type = {document.document_type: document for document in documents}
    if len(by_type) != len(documents):
        raise ValidationError("document types must be unique")
    missing = REQUIRED_TYPES - set(by_type)
    if missing:
        raise ValidationError(f"missing document types: {', '.join(sorted(missing))}")
    invoice = by_type["commercial_invoice"]
    packing = by_type["packing_list"]
    origin = by_type["origin_certificate"]
    findings: list[Finding] = []
    for left, right, code, label in [
        (
            _field(invoice, "purchase_order"),
            _field(packing, "purchase_order"),
            "purchase_order_mismatch",
            "Purchase order",
        ),
        (_field(invoice, "supplier"), _field(packing, "supplier"), "supplier_mismatch", "Supplier"),
        (_field(invoice, "sku_1"), _field(packing, "sku_1"), "sku_mismatch", "SKU"),
        (
            _field(invoice, "quantity_1"),
            _field(packing, "quantity_1"),
            "quantity_mismatch",
            "Quantity",
        ),
        (
            _field(invoice, "country_of_origin"),
            _field(origin, "country_of_origin"),
            "origin_mismatch",
            "Country of origin",
        ),
    ]:
        finding = _compare(left, right, code, label)
        if finding:
            findings.append(finding)
    quantity = decimal_value(_field(invoice, "quantity_1").value, "quantity_1")
    unit_price = decimal_value(_field(invoice, "unit_price_1").value, "unit_price_1")
    total = decimal_value(_field(invoice, "line_total_1").value, "line_total_1")
    if quantity * unit_price != total:
        findings.append(
            Finding(
                "invoice_math_mismatch",
                "block",
                f"Invoice line math mismatch: {quantity} x {unit_price} != {total}",
                (f"page {_field(invoice, 'line_total_1').page}",),
            )
        )
    for document in documents:
        low = [field.name for field in document.fields if field.confidence < MIN_CONFIDENCE]
        if low:
            findings.append(
                Finding(
                    "low_confidence",
                    "review",
                    f"{document.document_type} has low-confidence fields: {', '.join(low)}",
                    (document.sha256,),
                )
            )
    sorted_documents = sorted(documents, key=lambda item: item.document_type)
    evidence_seed = json.dumps(
        [
            {
                "document_id": item.document_id,
                "document_type": item.document_type,
                "sha256": item.sha256,
                "provider": item.provider,
            }
            for item in sorted_documents
        ],
        sort_keys=True,
    )
    audit_hash = hashlib.sha256(evidence_seed.encode()).hexdigest()
    status = "ready_for_human_approval" if not findings else "human_review_required"
    return {
        "status": status,
        "auto_released": False,
        "document_count": len(documents),
        "provider_mode": "simulation"
        if all(item.provider == "synthetic_fixture" for item in documents)
        else "live",
        "audit_hash": audit_hash,
        "findings": [asdict(finding) for finding in findings],
        "documents": [
            {
                "document_id": item.document_id,
                "document_type": item.document_type,
                "sha256": item.sha256,
                "provider": item.provider,
            }
            for item in sorted_documents
        ],
    }
