from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

DOC_TYPES = {"commercial_invoice", "packing_list", "origin_certificate"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{1,79}$")


class ValidationError(ValueError):
    """Input or provider output is outside the accepted contract."""


def decimal_value(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field} must be numeric") from exc
    if not result.is_finite():
        raise ValidationError(f"{field} must be finite")
    return result


@dataclass(frozen=True)
class EvidenceField:
    name: str
    value: str
    confidence: Decimal
    page: int

    @classmethod
    def from_dict(cls, payload: Any) -> EvidenceField:
        if not isinstance(payload, dict):
            raise ValidationError("each field must be an object")
        name = payload.get("name")
        value = payload.get("value")
        if not isinstance(name, str) or not SAFE_ID.fullmatch(name):
            raise ValidationError("field name must be a stable identifier")
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 300:
            raise ValidationError("field value must be 1-300 characters")
        confidence = decimal_value(payload.get("confidence"), "confidence")
        if not Decimal("0") <= confidence <= Decimal("1"):
            raise ValidationError("confidence must be between 0 and 1")
        page = payload.get("page")
        if type(page) is not int or page < 1:
            raise ValidationError("page must be a positive integer")
        return cls(name, value.strip(), confidence, page)


@dataclass(frozen=True)
class ExtractedDocument:
    document_id: str
    document_type: str
    sha256: str
    fields: tuple[EvidenceField, ...]
    provider: str

    @classmethod
    def from_dict(cls, payload: Any) -> ExtractedDocument:
        if not isinstance(payload, dict):
            raise ValidationError("document extraction must be an object")
        document_id = payload.get("document_id")
        document_type = payload.get("document_type")
        sha256 = payload.get("sha256")
        provider = payload.get("provider")
        if not isinstance(document_id, str) or not SAFE_ID.fullmatch(document_id):
            raise ValidationError("document_id must be a stable identifier")
        if document_type not in DOC_TYPES:
            raise ValidationError("unsupported document_type")
        if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise ValidationError("sha256 must be lowercase hexadecimal")
        if provider not in {"nutrient_dws", "synthetic_fixture"}:
            raise ValidationError("unsupported extraction provider")
        fields_raw = payload.get("fields")
        if not isinstance(fields_raw, list) or not fields_raw:
            raise ValidationError("fields must be a non-empty list")
        fields = tuple(EvidenceField.from_dict(item) for item in fields_raw)
        if len({field.name for field in fields}) != len(fields):
            raise ValidationError("field names must be unique per document")
        return cls(document_id, document_type, sha256, fields, provider)

    def values(self) -> dict[str, EvidenceField]:
        return {field.name: field for field in self.fields}
