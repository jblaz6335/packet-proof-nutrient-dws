from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .engine import reconcile_packet
from .models import ValidationError
from .provider import FixtureProvider, NutrientProvider
from .report import write_report

LIVE_CONFIRMATION = "PROCESS THREE SYNTHETIC DOCUMENTS"
DOCUMENTS = [
    ("commercial-invoice", "commercial_invoice", "commercial-invoice.pdf"),
    ("packing-list", "packing_list", "packing-list.pdf"),
    ("origin-certificate", "origin_certificate", "origin-certificate.pdf"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="packet-proof")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo")
    demo.add_argument("--fixture-dir", default="fixtures/extractions")
    demo.add_argument("--pdf-dir", default="output/pdf")
    demo.add_argument("--output-dir", default="artifacts")
    live = subparsers.add_parser("extract-live")
    live.add_argument("--pdf-dir", default="output/pdf")
    live.add_argument("--output-dir", default="artifacts/live")
    live.add_argument("--execute", action="store_true")
    live.add_argument("--confirm")
    return parser


def run(args: argparse.Namespace) -> dict:
    if args.command == "demo":
        provider = FixtureProvider(args.fixture_dir)
    else:
        if not args.execute or args.confirm != LIVE_CONFIRMATION:
            raise PermissionError(
                f'live extraction requires --execute --confirm "{LIVE_CONFIRMATION}"'
            )
        provider = NutrientProvider(os.environ.get("NUTRIENT_API_KEY", ""))
    pdf_dir = Path(args.pdf_dir)
    documents = [
        provider.extract(pdf_dir / filename, document_id, document_type)
        for document_id, document_type, filename in DOCUMENTS
    ]
    result = reconcile_packet(documents)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "packet-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_report(result, output / "packet-report.html")
    return {
        "status": result["status"],
        "provider_mode": result["provider_mode"],
        "document_count": result["document_count"],
        "finding_count": len(result["findings"]),
        "auto_released": result["auto_released"],
        "report": str(output / "packet-report.html"),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(json.dumps(run(args), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, ValidationError, PermissionError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
