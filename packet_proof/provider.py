from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Protocol

import httpx

from .models import ExtractedDocument, ValidationError

OFFICIAL_BASE_URL = "https://api.nutrient.io"


class ExtractionProvider(Protocol):
    is_simulation: bool

    def extract(self, path: Path, document_id: str, document_type: str) -> ExtractedDocument: ...


class NutrientProvider:
    """Server-side adapter for Nutrient DWS Processor API JSON extraction."""

    is_simulation = False

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = OFFICIAL_BASE_URL,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key or any(character.isspace() for character in api_key):
            raise ValueError("NUTRIENT_API_KEY must be non-empty and contain no whitespace")
        if base_url != OFFICIAL_BASE_URL:
            raise ValueError("NUTRIENT_BASE_URL must use the official HTTPS origin")
        self._api_key = api_key
        self._client = client or httpx.Client(timeout=60)
        self._base_url = base_url

    def extract(self, path: Path, document_id: str, document_type: str) -> ExtractedDocument:
        content = path.read_bytes()
        instructions = {
            "parts": [{"file": "document"}],
            "output": {
                "type": "json-content",
                "plainText": True,
                "structuredText": True,
                "keyValuePairs": True,
                "tables": True,
            },
        }
        response = self._client.post(
            f"{self._base_url}/build",
            headers={"Authorization": f"Bearer {self._api_key}"},
            files={
                "document": (path.name, content, "application/pdf"),
                "instructions": (None, json.dumps(instructions), "application/json"),
            },
        )
        response.raise_for_status()
        payload = response.json()
        return self._normalize(
            payload, document_id, document_type, hashlib.sha256(content).hexdigest()
        )

    @staticmethod
    def _normalize(
        payload: Any, document_id: str, document_type: str, sha256: str
    ) -> ExtractedDocument:
        if not isinstance(payload, dict):
            raise ValidationError("Nutrient response must be a JSON object")
        pages = payload.get("pages")
        page_pairs: list[dict[str, Any]] = []
        page_text: list[tuple[int, str]] = []
        if isinstance(pages, list):
            for page_number, page in enumerate(pages, start=1):
                if not isinstance(page, dict):
                    raise ValidationError("Nutrient page must be an object")
                pairs = page.get("keyValuePairs") or page.get("key_value_pairs") or []
                if not isinstance(pairs, list):
                    raise ValidationError("Nutrient key-value pairs must be a list")
                for pair in pairs:
                    if isinstance(pair, dict) and "page" not in pair:
                        pair = {**pair, "page": page_number}
                    page_pairs.append(pair)
                plain_text = page.get("plainText") or page.get("plain_text")
                if isinstance(plain_text, str):
                    page_text.append((page_number, plain_text))
        raw_pairs = payload.get("keyValuePairs") or payload.get("key_value_pairs") or page_pairs
        if not isinstance(raw_pairs, list) or not raw_pairs:
            raise ValidationError("Nutrient response did not include key-value pairs")
        fields = []
        pair_names: set[str] = set()
        for item in raw_pairs:
            if not isinstance(item, dict):
                raise ValidationError("Nutrient key-value pair must be an object")
            key = item.get("key")
            value = item.get("value")
            if isinstance(key, dict):
                key = key.get("text") or key.get("content")
            if isinstance(value, dict):
                value = value.get("text") or value.get("content")
            if key is None or value is None:
                raise ValidationError("Nutrient key-value pair must include key and value text")
            name = re.sub(r"[^a-z0-9]+", "_", str(key).strip().lower()).strip("_")
            if not name or name in pair_names:
                continue
            normalized_value = str(value).strip()
            if name == "country_of_origin":
                normalized_value = re.sub(
                    r"\bS\$\s*tates\b", "States", normalized_value, flags=re.IGNORECASE
                )
            confidence = item.get("confidence", 0)
            if isinstance(confidence, (int, float)) and confidence > 1:
                confidence /= 100
            fields.append(
                {
                    "name": name,
                    "value": normalized_value,
                    "confidence": confidence,
                    "page": item.get("page", 1),
                }
            )
            pair_names.add(name)
        existing = {field["name"] for field in fields}
        for page_number, text in page_text:
            country = re.search(r"(?mi)^\s*Country of origin\s{2,}([^\r\n]+?)\s*$", text)
            if country:
                country_value = re.sub(
                    r"\bS\$?\s*tates\b", "States", country.group(1), flags=re.IGNORECASE
                ).strip()
                fields = [field for field in fields if field["name"] != "country_of_origin"]
                fields.append(
                    {
                        "name": "country_of_origin",
                        "value": country_value,
                        "confidence": 0.95,
                        "page": page_number,
                    }
                )
                existing.add("country_of_origin")
            invoice_row = re.search(
                r"(?m)^\s*([A-Z]{2}-\d{3})\s+.+?\s+(\d+)\s+\$?([\d,]+\.\d{2})\s+\$?([\d,]+\.\d{2})\s*$",
                text,
            )
            packing_row = re.search(
                r"(?m)^\s*([A-Z]{2}-\d{3})\s{2,}.+?\s{2,}(\d+)(?:\s{2,}\d+)?\s*$",
                text,
            )
            row = invoice_row or packing_row
            if row:
                derived = {
                    "sku_1": row.group(1),
                    "quantity_1": row.group(2),
                }
                if invoice_row:
                    derived.update(
                        {
                            "unit_price_1": row.group(3).replace(",", ""),
                            "line_total_1": row.group(4).replace(",", ""),
                        }
                    )
                for name, value in derived.items():
                    if name not in existing:
                        fields.append(
                            {
                                "name": name,
                                "value": value,
                                "confidence": 1,
                                "page": page_number,
                            }
                        )
                        existing.add(name)
        return ExtractedDocument.from_dict(
            {
                "document_id": document_id,
                "document_type": document_type,
                "sha256": sha256,
                "provider": "nutrient_dws",
                "fields": fields,
            }
        )


class FixtureProvider:
    is_simulation = True

    def __init__(self, fixture_dir: str | Path) -> None:
        self.fixture_dir = Path(fixture_dir)
        self.calls: list[str] = []

    def extract(self, path: Path, document_id: str, document_type: str) -> ExtractedDocument:
        self.calls.append(document_id)
        payload = json.loads((self.fixture_dir / f"{document_id}.json").read_text(encoding="utf-8"))
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        payload.update(
            {
                "document_id": document_id,
                "document_type": document_type,
                "sha256": actual_hash,
                "provider": "synthetic_fixture",
            }
        )
        return ExtractedDocument.from_dict(payload)
