"""Render the Packet Proof narration with the local Kokoro ONNX voice."""

from __future__ import annotations

from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro

ASSET_DIR = Path(__file__).resolve().parent
NARRATION = (
    "A shipment packet can look complete and still disagree on the facts that determine release. Packet Proof catches those discrepancies before they become an expensive downstream surprise. It is an auditable exception desk for trade document packets, built for the Nutrient D W S challenge.",
    "The demonstration starts with three polished, fictional documents: a commercial invoice, a packing list, and a certificate of origin. The invoice states twenty four A X four ten units. The packing list states twenty two. The certificate provides the origin evidence. A human reviewer should not have to hunt across pages to discover that disagreement.",
    "Nutrient D W S performs the core document operation. Packet Proof sends each P D F to the official build endpoint and requests structured J son content, including plain text, key value pairs, and tables. The provider response is treated as evidence, not authority. Required fields, confidence values, document identity, and response shape are validated. Uncertainty fails closed.",
    "Packet Proof then reconciles the extracted fields with deterministic rules. It checks packet identity, supplier, S K U, quantity, country of origin, invoice arithmetic, and extraction confidence. The reproducible replay processes all three documents and produces one blocking quantity mismatch. The status is human review required, and automatic release is false. The implementation has eighty automated tests and ninety five point four eight percent branch aware coverage.",
    "The exception desk ties the finding back to both source documents. It shows twenty four units on the invoice and twenty two on the packing list. It records page evidence, preserves an S H A two fifty six hash for every input, and creates a stable audit hash for the complete run. The result can be replayed from the same evidence instead of asking anyone to trust an opaque answer.",
    "The boundary is the product. Packet Proof extracts and normalizes evidence, compares every required field, surfaces confidence and mismatches, and preserves the audit trail. It does not release, sign, amend, transmit, or represent a customs decision. Nutrient D W S extracted structured J son content from each source P D F. Packet Proof reconciled those extracted fields deterministically and reserved the release decision for a human.",
)


def main() -> None:
    model = Kokoro(
        str(ASSET_DIR / "kokoro-v1.0.onnx"),
        str(ASSET_DIR / "voices-v1.0.bin"),
    )
    for index, text in enumerate(NARRATION, start=1):
        samples, sample_rate = model.create(
            text,
            voice="af_heart",
            speed=1.03,
            lang="en-us",
        )
        sf.write(ASSET_DIR / f"slide-{index}.wav", samples, sample_rate)
        print(f"rendered slide-{index}.wav")


if __name__ == "__main__":
    main()
