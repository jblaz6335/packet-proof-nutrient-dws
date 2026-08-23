from __future__ import annotations

import hashlib
import json
from decimal import Decimal

import httpx
import pytest

from packet_proof.models import ValidationError
from packet_proof.provider import OFFICIAL_BASE_URL, FixtureProvider, NutrientProvider

from .conftest import document_payload


def test_fixture_provider_hashes_real_pdf_and_records_call(tmp_path):
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    payload = document_payload("packing_list")
    for key in ("document_id", "document_type", "sha256", "provider"):
        payload.pop(key)
    (fixture_dir / "packing-list.json").write_text(json.dumps(payload), encoding="utf-8")
    pdf = tmp_path / "packing-list.pdf"
    pdf.write_bytes(b"%PDF-synthetic")
    provider = FixtureProvider(fixture_dir)
    document = provider.extract(pdf, "packing-list", "packing_list")
    assert document.sha256 == hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert document.provider == "synthetic_fixture"
    assert provider.calls == ["packing-list"]


@pytest.mark.parametrize("api_key", ["", "has whitespace", "\t"])
def test_nutrient_provider_rejects_bad_api_key(api_key):
    with pytest.raises(ValueError, match="API_KEY"):
        NutrientProvider(api_key)


def test_nutrient_provider_rejects_nonofficial_origin():
    with pytest.raises(ValueError, match="official HTTPS origin"):
        NutrientProvider("secret", base_url="https://example.com")


def test_nutrient_provider_posts_exact_build_request(tmp_path):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(
            200,
            json={
                "keyValuePairs": [
                    {
                        "key": {"text": "Purchase Order"},
                        "value": {"text": "PO-8814"},
                        "confidence": 0.98,
                        "page": 2,
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    pdf = tmp_path / "invoice.pdf"
    pdf.write_bytes(b"%PDF-test")
    provider = NutrientProvider("secret-token", client=client)
    document = provider.extract(pdf, "commercial-invoice", "commercial_invoice")
    request = captured["request"]
    assert str(request.url) == f"{OFFICIAL_BASE_URL}/build"
    assert request.headers["Authorization"] == "Bearer secret-token"
    body = request.content
    assert b'"type": "json-content"' in body
    assert b'"keyValuePairs": true' in body
    assert b"%PDF-test" in body
    assert document.values()["purchase_order"].page == 2
    assert document.provider == "nutrient_dws"


def test_nutrient_provider_raises_http_errors(tmp_path):
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(401, request=request))
    )
    pdf = tmp_path / "invoice.pdf"
    pdf.write_bytes(b"%PDF-test")
    with pytest.raises(httpx.HTTPStatusError):
        NutrientProvider("secret", client=client).extract(
            pdf, "commercial-invoice", "commercial_invoice"
        )


@pytest.mark.parametrize("payload", [[], {}, {"keyValuePairs": []}])
def test_nutrient_normalize_rejects_missing_pairs(payload):
    with pytest.raises(ValidationError):
        NutrientProvider._normalize(payload, "invoice", "commercial_invoice", "a" * 64)


def test_nutrient_normalize_accepts_snake_case_pairs():
    document = NutrientProvider._normalize(
        {
            "key_value_pairs": [
                {"key": "Supplier", "value": "Northstar", "confidence": 1, "page": 1}
            ]
        },
        "invoice",
        "commercial_invoice",
        "a" * 64,
    )
    assert document.values()["supplier"].value == "Northstar"


def test_nutrient_normalize_accepts_current_page_schema_and_derives_line_item():
    document = NutrientProvider._normalize(
        {
            "pages": [
                {
                    "keyValuePairs": [
                        {
                            "key": {"content": "Purchase order"},
                            "value": {"content": "PO-8814"},
                            "confidence": 98,
                        }
                    ],
                    "plainText": "AX-410  Control module  24  $120.00  $2,880.00",
                }
            ]
        },
        "invoice",
        "commercial_invoice",
        "a" * 64,
    )
    assert document.values()["purchase_order"].confidence == Decimal("0.98")
    assert document.values()["purchase_order"].page == 1
    assert document.values()["sku_1"].value == "AX-410"
    assert document.values()["quantity_1"].value == "24"
    assert document.values()["unit_price_1"].value == "120.00"
    assert document.values()["line_total_1"].value == "2880.00"


def test_nutrient_normalize_uses_labeled_country_and_packed_quantity():
    document = NutrientProvider._normalize(
        {
            "pages": [
                {
                    "keyValuePairs": [
                        {
                            "key": {"content": "Country of origin"},
                            "value": {"content": "Destination"},
                            "confidence": 100,
                        }
                    ],
                    "plainText": (
                        "Country of origin       United S$ tates\n"
                        "AX-410    Control module                22        3\n"
                    ),
                }
            ]
        },
        "packing",
        "packing_list",
        "a" * 64,
    )
    assert document.values()["country_of_origin"].value == "United States"
    assert document.values()["quantity_1"].value == "22"


def test_nutrient_normalize_rejects_nonobject_pair():
    with pytest.raises(ValidationError, match="must be an object"):
        NutrientProvider._normalize(
            {"keyValuePairs": ["bad"]}, "invoice", "commercial_invoice", "a" * 64
        )
