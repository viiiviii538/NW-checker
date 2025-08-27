from pypdf import PdfReader
from src.report.pdf import create_pdf


def test_create_pdf(tmp_path):
    report_data = {
        "findings": {
            "ports": {"score": 50, "details": {"note": "ok"}},
            "vulns": {"score": 90, "details": {"issue": "CVE-1234"}},
        },
        "risk_score": 75,
    }
    output = tmp_path / "report.pdf"
    create_pdf(report_data, str(output))
    assert output.exists()

    reader = PdfReader(str(output))
    text = "".join(page.extract_text() for page in reader.pages)
    assert "Static Scan Report" in text
    assert "Generated:" in text
    assert "Overall Risk Score: 75" in text
    assert "ports: 50" in text
    assert "note: ok" in text
    assert "vulns: 90 HIGH RISK" in text
    assert "issue: CVE-1234" in text
