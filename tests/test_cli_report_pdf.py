from __future__ import annotations

import argparse
import json

import pytest
from pypdf import PdfReader

from packet_proof import cli
from packet_proof.report import write_report

from .conftest import document_payload


def _demo_tree(tmp_path):
    pdf_dir = tmp_path / "pdf"
    fixture_dir = tmp_path / "fixtures"
    pdf_dir.mkdir()
    fixture_dir.mkdir()
    for document_id, document_type, filename in cli.DOCUMENTS:
        (pdf_dir / filename).write_bytes(b"%PDF synthetic " + document_id.encode())
        payload = document_payload(document_type)
        for key in ("document_id", "document_type", "sha256", "provider"):
            payload.pop(key)
        (fixture_dir / f"{document_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    return pdf_dir, fixture_dir


def test_demo_cli_writes_json_and_html(tmp_path):
    pdf_dir, fixture_dir = _demo_tree(tmp_path)
    output = tmp_path / "artifacts"
    args = argparse.Namespace(
        command="demo", fixture_dir=fixture_dir, pdf_dir=pdf_dir, output_dir=output
    )
    summary = cli.run(args)
    assert summary["status"] == "ready_for_human_approval"
    assert summary["provider_mode"] == "simulation"
    assert summary["auto_released"] is False
    assert (output / "packet-result.json").is_file()
    assert "Human authority" in (output / "packet-report.html").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("execute", "confirmation"),
    [(False, None), (True, None), (True, "wrong")],
)
def test_live_cli_requires_two_part_gate(execute, confirmation):
    args = argparse.Namespace(
        command="extract-live",
        execute=execute,
        confirm=confirmation,
        pdf_dir="output/pdf",
        output_dir="artifacts/live",
    )
    with pytest.raises(PermissionError, match="live extraction requires"):
        cli.run(args)


def test_main_returns_two_on_operational_error(monkeypatch, capsys):
    monkeypatch.setattr(cli, "run", lambda args: (_ for _ in ()).throw(PermissionError("blocked")))
    assert cli.main(["demo"]) == 2
    assert "error: blocked" in capsys.readouterr().err


def test_main_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli, "run", lambda args: {"status": "ok"})
    assert cli.main(["demo"]) == 0
    assert json.loads(capsys.readouterr().out) == {"status": "ok"}


def test_report_escapes_untrusted_values(tmp_path):
    result = {
        "document_count": 1,
        "provider_mode": "simulation",
        "audit_hash": "a" * 64,
        "findings": [
            {"severity": "block", "code": "<script>", "message": "<b>unsafe</b>", "evidence": []}
        ],
        "documents": [
            {
                "document_type": "commercial_invoice",
                "document_id": "<id>",
                "sha256": "a" * 64,
                "provider": "synthetic_fixture",
            }
        ],
    }
    path = tmp_path / "report.html"
    write_report(result, path)
    html = path.read_text(encoding="utf-8")
    assert "&lt;script&gt;" in html
    assert "<script>" not in html
    assert "&lt;b&gt;unsafe&lt;/b&gt;" in html


def test_report_empty_findings_message(tmp_path):
    result = {
        "document_count": 0,
        "provider_mode": "simulation",
        "audit_hash": "a" * 64,
        "findings": [],
        "documents": [],
    }
    path = tmp_path / "report.html"
    write_report(result, path)
    assert "No deterministic mismatches found" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("filename", "required_text"),
    [
        ("commercial-invoice.pdf", "Commercial Invoice"),
        ("packing-list.pdf", "Packing List"),
        ("origin-certificate.pdf", "Certificate of Origin"),
    ],
)
def test_demo_pdfs_are_single_page_and_labeled(filename, required_text):
    path = cli.Path(__file__).resolve().parents[1] / "output" / "pdf" / filename
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert required_text in text
    assert "FICTIONAL SYNTHETIC HACKATHON FIXTURE" in text
