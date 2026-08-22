from __future__ import annotations

import hashlib
import json
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
        raw_pairs = payload.get("keyValuePairs") or payload.get("key_value_pairs")
        if not isinstance(raw_pairs, list) or not raw_pairs:
            raise ValidationError("Nutrient response did not include key-value pairs")
        fields = []
        for item in raw_pairs:
            if not isinstance(item, dict):
                raise ValidationError("Nutrient key-value pair must be an object")
            key = item.get("key")
            value = item.get("value")
            if isinstance(key, dict):
                key = key.get("text")
            if isinstance(value, dict):
                value = value.get("text")
            fields.append(
                {
                    "name": str(key).strip().lower().replace(" ", "_"),
                    "value": str(value).strip(),
                    "confidence": item.get("confidence", 0),
                    "page": item.get("page", 1),
                }
            )
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
