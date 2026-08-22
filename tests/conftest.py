from __future__ import annotations

import hashlib
from copy import deepcopy

import pytest

from packet_proof.models import ExtractedDocument

BASE_FIELDS = {
    "commercial_invoice": [
        ("supplier", "Northstar Components LLC"),
        ("purchase_order", "PO-8814"),
        ("currency", "USD"),
        ("country_of_origin", "United States"),
        ("sku_1", "AX-410"),
        ("quantity_1", "24"),
        ("unit_price_1", "120.00"),
        ("line_total_1", "2880.00"),
    ],
    "packing_list": [
        ("supplier", "Northstar Components LLC"),
        ("purchase_order", "PO-8814"),
        ("sku_1", "AX-410"),
        ("quantity_1", "24"),
    ],
    "origin_certificate": [
        ("country_of_origin", "United States"),
        ("purchase_order", "PO-8814"),
    ],
}


def document_payload(document_type: str, *, provider: str = "synthetic_fixture") -> dict:
    return {
        "document_id": document_type.replace("_", "-"),
        "document_type": document_type,
        "sha256": hashlib.sha256(document_type.encode()).hexdigest(),
        "provider": provider,
        "fields": [
            {"name": name, "value": value, "confidence": 0.99, "page": 1}
            for name, value in BASE_FIELDS[document_type]
        ],
    }


def packet_payloads() -> list[dict]:
    return [document_payload(document_type) for document_type in BASE_FIELDS]


def mutate_field(payload: dict, name: str, **changes) -> dict:
    result = deepcopy(payload)
    field = next(item for item in result["fields"] if item["name"] == name)
    field.update(changes)
    return result


@pytest.fixture
def clean_documents() -> list[ExtractedDocument]:
    return [ExtractedDocument.from_dict(payload) for payload in packet_payloads()]
