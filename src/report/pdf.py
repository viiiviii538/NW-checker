"""PDF reporting for scan results."""

from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

HIGH_RISK_THRESHOLD = 70


def create_pdf(report_data: Dict[str, Any], output_path: str) -> None:
    """Render scan results into a PDF.

    Args:
        report_data: 結果の辞書。"findings"キーを含む場合はその値を使用。
        output_path: 出力PDFファイルのパス。
    """
    findings = report_data.get("findings", report_data)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Static Scan Report")
    y -= 24

    c.setFont("Helvetica", 12)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(40, y, f"Generated: {timestamp}")
    y -= 30

    for category, data in findings.items():
        score = data.get("score")
        high_risk = score is not None and score >= HIGH_RISK_THRESHOLD
        text = f"{category}: {score}" + (" HIGH RISK" if high_risk else "")
        c.drawString(40, y, text)
        y -= 18
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
