from __future__ import annotations

"""HTTP server exposing the static scan API."""

import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from . import static_scan
from .report.pdf import create_pdf

STATIC_SCAN_TIMEOUT = 60  # seconds
REPORT_PATH = "/tmp/static_scan_report.pdf"

app = FastAPI()


@app.get("/static_scan")
async def static_scan_endpoint(report: bool = False):
    """Run all static scan modules and return aggregated results.

    Parameters
    ----------
    report: bool, optional
        When ``True`` the server generates a PDF report and returns its path.
    """

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(static_scan.run_all),
            timeout=STATIC_SCAN_TIMEOUT,
        )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"status": "timeout", "message": "Static scan timed out"},
        )
    except Exception as exc:  # pylint: disable=broad-except
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Static scan failed: {exc}"},
        )

    findings = result.get("findings", {}) if isinstance(result, dict) else result
    risk_score = result.get("risk_score") if isinstance(result, dict) else None

    response = {"status": "ok", "findings": findings, "risk_score": risk_score}
    if report:
        create_pdf(result, REPORT_PATH)
        response["report_path"] = REPORT_PATH
    return response
