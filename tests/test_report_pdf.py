from pypdf import PdfReader
from src.report.pdf import create_pdf


def test_create_pdf(tmp_path):
    report_data = {
        "findings": {
            "ports": {"score": 50},
            "vulns": {"score": 90},
        }
    }
    output = tmp_path / "report.pdf"
    create_pdf(report_data, str(output))
    assert output.exists()

    reader = PdfReader(str(output))
    text = "".join(page.extract_text() for page in reader.pages)
    assert "Static Scan Report" in text
    assert "Generated:" in text
    assert "ports: 50" in text
    assert "vulns: 90 HIGH RISK" in text
