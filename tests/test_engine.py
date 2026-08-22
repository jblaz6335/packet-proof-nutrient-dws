from __future__ import annotations

from copy import deepcopy

import pytest

from packet_proof.engine import reconcile_packet
from packet_proof.models import ExtractedDocument, ValidationError

from .conftest import document_payload, mutate_field, packet_payloads


def documents_from(payloads):
    return [ExtractedDocument.from_dict(payload) for payload in payloads]


def replace_document(payloads, changed):
    return [
        changed if item["document_type"] == changed["document_type"] else item for item in payloads
    ]


def test_clean_packet_is_ready_but_never_auto_released(clean_documents):
    result = reconcile_packet(clean_documents)
    assert result["status"] == "ready_for_human_approval"
    assert result["auto_released"] is False
    assert result["findings"] == []
    assert result["provider_mode"] == "simulation"
    assert result["document_count"] == 3


@pytest.mark.parametrize(
    ("document_type", "field", "value", "code"),
    [
        ("packing_list", "purchase_order", "PO-9999", "purchase_order_mismatch"),
        ("packing_list", "supplier", "Other Supplier", "supplier_mismatch"),
        ("packing_list", "sku_1", "ZZ-999", "sku_mismatch"),
        ("packing_list", "quantity_1", "22", "quantity_mismatch"),
        ("origin_certificate", "country_of_origin", "Canada", "origin_mismatch"),
    ],
)
def test_cross_document_mismatches_require_review(document_type, field, value, code):
    payloads = packet_payloads()
    changed = mutate_field(document_payload(document_type), field, value=value, page=3)
    result = reconcile_packet(documents_from(replace_document(payloads, changed)))
    assert result["status"] == "human_review_required"
    assert result["findings"][0]["code"] == code
    assert "page 3" in result["findings"][0]["evidence"]


def test_invoice_math_mismatch_is_blocking():
    payloads = packet_payloads()
    changed = mutate_field(document_payload("commercial_invoice"), "line_total_1", value="2879")
    result = reconcile_packet(documents_from(replace_document(payloads, changed)))
    assert result["findings"][0]["code"] == "invoice_math_mismatch"
    assert result["findings"][0]["severity"] == "block"


def test_low_confidence_is_review_finding():
    payloads = packet_payloads()
    changed = mutate_field(document_payload("packing_list"), "supplier", confidence=0.89)
    result = reconcile_packet(documents_from(replace_document(payloads, changed)))
    assert result["findings"] == [
        {
            "code": "low_confidence",
            "severity": "review",
            "message": "packing_list has low-confidence fields: supplier",
            "evidence": (changed["sha256"],),
        }
    ]


def test_confidence_at_threshold_is_accepted():
    payloads = packet_payloads()
    changed = mutate_field(document_payload("packing_list"), "supplier", confidence=0.90)
    result = reconcile_packet(documents_from(replace_document(payloads, changed)))
    assert result["findings"] == []


def test_live_provider_marks_result_live():
    payloads = packet_payloads()
    payloads[0]["provider"] = "nutrient_dws"
    assert reconcile_packet(documents_from(payloads))["provider_mode"] == "live"


def test_audit_hash_is_deterministic_across_input_order(clean_documents):
    first = reconcile_packet(clean_documents)["audit_hash"]
    second = reconcile_packet(list(reversed(clean_documents)))["audit_hash"]
    assert first == second


def test_audit_hash_changes_with_document_hash(clean_documents):
    baseline = reconcile_packet(clean_documents)["audit_hash"]
    payloads = packet_payloads()
    payloads[0]["sha256"] = "f" * 64
    changed = reconcile_packet(documents_from(payloads))["audit_hash"]
    assert changed != baseline


def test_duplicate_document_type_rejected(clean_documents):
    with pytest.raises(ValidationError, match="must be unique"):
        reconcile_packet([*clean_documents, clean_documents[0]])


def test_missing_document_type_rejected(clean_documents):
    with pytest.raises(ValidationError, match="origin_certificate"):
        reconcile_packet(clean_documents[:2])


def test_missing_required_field_rejected():
    payloads = packet_payloads()
    changed = deepcopy(document_payload("packing_list"))
    changed["fields"] = [item for item in changed["fields"] if item["name"] != "sku_1"]
    with pytest.raises(ValidationError, match="missing required field sku_1"):
        reconcile_packet(documents_from(replace_document(payloads, changed)))


def test_non_numeric_invoice_value_rejected():
    payloads = packet_payloads()
    changed = mutate_field(document_payload("commercial_invoice"), "unit_price_1", value="free")
    with pytest.raises(ValidationError, match="unit_price_1 must be numeric"):
        reconcile_packet(documents_from(replace_document(payloads, changed)))
