from __future__ import annotations

from decimal import Decimal

import pytest

from packet_proof.models import EvidenceField, ExtractedDocument, ValidationError, decimal_value

from .conftest import document_payload, mutate_field


@pytest.mark.parametrize("value", ["12.5", 4, Decimal("3.2")])
def test_decimal_value_accepts_numeric_values(value):
    assert decimal_value(value, "amount") == Decimal(str(value))


@pytest.mark.parametrize("value", ["not-number", object(), None])
def test_decimal_value_rejects_invalid_values(value):
    with pytest.raises(ValidationError, match="must be numeric"):
        decimal_value(value, "amount")


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_decimal_value_rejects_non_finite_values(value):
    with pytest.raises(ValidationError, match="must be finite"):
        decimal_value(value, "amount")


def test_evidence_field_parses_and_trims():
    field = EvidenceField.from_dict(
        {"name": "purchase_order", "value": " PO-8814 ", "confidence": "0.95", "page": 2}
    )
    assert field.value == "PO-8814"
    assert field.confidence == Decimal("0.95")
    assert field.page == 2


@pytest.mark.parametrize("payload", [None, [], "field"])
def test_evidence_field_requires_object(payload):
    with pytest.raises(ValidationError, match="must be an object"):
        EvidenceField.from_dict(payload)


@pytest.mark.parametrize("name", [None, "", " space", "x" * 81])
def test_evidence_field_rejects_bad_names(name):
    with pytest.raises(ValidationError, match="stable identifier"):
        EvidenceField.from_dict({"name": name, "value": "ok", "confidence": 1, "page": 1})


@pytest.mark.parametrize("value", [None, "", " ", "x" * 301])
def test_evidence_field_rejects_bad_values(value):
    with pytest.raises(ValidationError, match="1-300"):
        EvidenceField.from_dict({"name": "field", "value": value, "confidence": 1, "page": 1})


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_evidence_field_rejects_confidence_outside_unit_interval(confidence):
    with pytest.raises(ValidationError, match="between 0 and 1"):
        EvidenceField.from_dict(
            {"name": "field", "value": "ok", "confidence": confidence, "page": 1}
        )


@pytest.mark.parametrize("page", [True, 0, -1, 1.5, "1"])
def test_evidence_field_rejects_bad_pages(page):
    with pytest.raises(ValidationError, match="positive integer"):
        EvidenceField.from_dict({"name": "field", "value": "ok", "confidence": 1, "page": page})


def test_document_parses_and_indexes_fields():
    document = ExtractedDocument.from_dict(document_payload("commercial_invoice"))
    assert document.values()["purchase_order"].value == "PO-8814"


@pytest.mark.parametrize("payload", [None, [], "document"])
def test_document_requires_object(payload):
    with pytest.raises(ValidationError, match="must be an object"):
        ExtractedDocument.from_dict(payload)


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("document_id", "?bad", "document_id"),
        ("document_type", "bill_of_lading", "unsupported document_type"),
        ("sha256", "ABC", "sha256"),
        ("provider", "unknown", "unsupported extraction provider"),
        ("fields", [], "non-empty list"),
    ],
)
def test_document_rejects_bad_top_level_values(key, value, message):
    payload = document_payload("commercial_invoice")
    payload[key] = value
    with pytest.raises(ValidationError, match=message):
        ExtractedDocument.from_dict(payload)


def test_document_rejects_duplicate_field_names():
    payload = document_payload("commercial_invoice")
    payload["fields"].append(payload["fields"][0].copy())
    with pytest.raises(ValidationError, match="unique"):
        ExtractedDocument.from_dict(payload)


def test_mutated_field_remains_parseable():
    payload = mutate_field(document_payload("packing_list"), "quantity_1", value="22")
    assert ExtractedDocument.from_dict(payload).values()["quantity_1"].value == "22"
