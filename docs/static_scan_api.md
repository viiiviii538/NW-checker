# Static Scan API

This endpoint triggers all static scan modules in the Python backend and aggregates their results.
It is designed for consumption by the Flutter client.

## Request

- **Method**: `GET`
- **Path**: `/static_scan`
- **Query Parameters**:
  - `report` *(optional, boolean)*: when `true`, a PDF report is generated and the response contains `report_path`.

## Successful Response

```json
{
  "status": "ok",
  "findings": { /* results from static_scan.run_all() */ },
  "risk_score": 42,
  "report_path": "/tmp/static_scan_report.pdf" // only when report=true
}
```

- `findings`: Aggregated findings from all scanners.
- `risk_score`: Sum of the individual scores.
- `report_path`: Path to the generated PDF report. Returned only when `report=true`.

## Error Responses

### Timeout
- **Status Code**: `504`
```json
{
  "status": "timeout",
  "message": "Static scan timed out"
}
```

### General Failure
- **Status Code**: `500`
```json
{
  "status": "error",
  "message": "Static scan failed: <details>"
}
```

The Flutter client should handle these states to provide appropriate user feedback.
