from __future__ import annotations

import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import static_scan

STATIC_SCAN_TIMEOUT = 60  # seconds

app = FastAPI()

@app.get('/static_scan')
async def static_scan_endpoint():
    try:
        result = await asyncio.wait_for(asyncio.to_thread(static_scan.run_all), timeout=STATIC_SCAN_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse(status_code=504, content={
            'status': 'timeout',
            'message': 'Static scan timed out'
        })
    except Exception as exc:  # pylint: disable=broad-except
        return JSONResponse(status_code=500, content={
            'status': 'error',
            'message': f'Static scan failed: {exc}'
        })

    findings = result.get('findings', {}) if isinstance(result, dict) else result
    risk_score = result.get('risk_score') if isinstance(result, dict) else None
    return {'status': 'ok', 'findings': findings, 'risk_score': risk_score}
