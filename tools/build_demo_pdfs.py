from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
NAVY = colors.HexColor("#0B1736")
BLUE = colors.HexColor("#2667FF")
CREAM = colors.HexColor("#F6F2E8")
LINE = colors.HexColor("#D7DCE8")


def header(title: str, label: str) -> list:
    styles = getSampleStyleSheet()
    return [
        Paragraph(
            label.upper(),
            ParagraphStyle(
                "label",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
                textColor=BLUE,
                spaceAfter=8,
                tracking=1.2,
            ),
        ),
        Paragraph(
            title,
            ParagraphStyle(
                "title",
                parent=styles["Title"],
                fontSize=25,
                leading=29,
                textColor=NAVY,
                alignment=0,
                spaceAfter=12,
            ),
        ),
        Paragraph(
            "FICTIONAL SYNTHETIC HACKATHON FIXTURE - NOT A COMMERCIAL DOCUMENT",
            ParagraphStyle(
                "notice",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#9A4B3D"),
                backColor=colors.HexColor("#FFE1DB"),
                borderPadding=7,
                spaceAfter=18,
            ),
        ),
    ]


def info_table(rows: list[list[str]]) -> Table:
    table = Table(rows, colWidths=[1.65 * inch, 4.85 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), CREAM),
                ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def line_table(rows: list[list[str]], widths: list[float]) -> Table:
    table = Table(rows, colWidths=[width * inch for width in widths])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def build(path: Path, story: list, footer: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story.extend(
        [
            Spacer(1, 22),
            Paragraph(
                footer,
                ParagraphStyle(
                    "footer",
                    parent=styles["Normal"],
                    fontSize=8,
                    leading=11,
                    textColor=colors.HexColor("#667089"),
                ),
            ),
        ]
    )
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        rightMargin=54,
        leftMargin=54,
        topMargin=48,
        bottomMargin=48,
        title=path.stem,
        author="Blaz Algo Systems - synthetic fixture",
    )
    doc.build(story)


def main() -> None:
    styles = getSampleStyleSheet()
    invoice = header("Commercial Invoice", "Packet Proof / Source 1 of 3")
    invoice += [
        info_table(
            [
                ["Supplier", "Northstar Components LLC"],
                ["Invoice", "INV-2048"],
                ["Purchase order", "PO-8814"],
                ["Currency", "USD"],
                ["Country of origin", "United States"],
                ["Ship to", "Fictional Harbor Imports, Long Beach, CA"],
            ]
        ),
        Spacer(1, 20),
        line_table(
            [
                ["SKU", "Description", "Quantity", "Unit price", "Line total"],
                ["AX-410", "Control module", "24", "$120.00", "$2,880.00"],
                ["BX-205", "Mounting kit", "12", "$35.00", "$420.00"],
            ],
            [0.9, 2.3, 0.8, 1.0, 1.1],
        ),
        Spacer(1, 12),
        Paragraph(
            "Invoice total: USD 3,300.00",
            ParagraphStyle(
                "total",
                parent=styles["Normal"],
                fontSize=12,
                leading=14,
                alignment=TA_RIGHT,
                textColor=NAVY,
                fontName="Helvetica-Bold",
            ),
        ),
    ]
    build(
        OUTPUT / "commercial-invoice.pdf",
        invoice,
        "Synthetic fixture. All entities, identifiers, values, and addresses are fictional and reserved for local evaluation.",
    )

    packing = header("Packing List", "Packet Proof / Source 2 of 3")
    packing += [
        info_table(
            [
                ["Supplier", "Northstar Components LLC"],
                ["Packing list", "PK-2048"],
                ["Purchase order", "PO-8814"],
                ["Packages", "4 cartons"],
                ["Gross weight", "186 kg"],
                ["Destination", "Fictional Harbor Imports, Long Beach, CA"],
            ]
        ),
        Spacer(1, 20),
        line_table(
            [
                ["SKU", "Description", "Packed quantity", "Cartons"],
                ["AX-410", "Control module", "22", "3"],
                ["BX-205", "Mounting kit", "12", "1"],
            ],
            [1.0, 3.0, 1.3, 1.0],
        ),
        Spacer(1, 14),
        Paragraph(
            "Exception intentionally embedded: AX-410 packing quantity is 22 while the commercial invoice states 24.",
            ParagraphStyle(
                "exception",
                parent=styles["Normal"],
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#9A4B3D"),
            ),
        ),
    ]
    build(
        OUTPUT / "packing-list.pdf",
        packing,
        "Synthetic fixture. The quantity mismatch is deliberate and is the expected deterministic review finding.",
    )

    certificate = header("Certificate of Origin", "Packet Proof / Source 3 of 3")
    certificate += [
        info_table(
            [
                ["Exporter", "Northstar Components LLC"],
                ["Certificate", "CO-7791"],
                ["Purchase order", "PO-8814"],
                ["Country of origin", "United States"],
                ["Destination", "United States"],
                ["Goods", "Electronic control modules and mounting kits"],
            ]
        ),
        Spacer(1, 20),
        Paragraph(
            "Declaration",
            ParagraphStyle(
                "section", parent=styles["Heading2"], fontSize=13, leading=16, textColor=NAVY
            ),
        ),
        Paragraph(
            "The undersigned fictional exporter declares that the goods described above originate in the United States. This page is a synthetic software-test fixture and is not a signed or legally operative certificate.",
            ParagraphStyle(
                "body", parent=styles["BodyText"], fontSize=10, leading=15, textColor=NAVY
            ),
        ),
        Spacer(1, 24),
        line_table(
            [
                ["Authorized representative", "Date", "Status"],
                ["Synthetic Fixture", "2026-08-22", "NOT SIGNED"],
            ],
            [2.8, 1.4, 1.8],
        ),
    ]
    build(
        OUTPUT / "origin-certificate.pdf",
        certificate,
        "Synthetic fixture. No signature, seal, certification, exporter, shipment, or commercial transaction is represented.",
    )


if __name__ == "__main__":
    main()
