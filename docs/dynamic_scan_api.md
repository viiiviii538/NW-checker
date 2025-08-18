# Dynamic Scan API

Endpoints to control and retrieve results from the dynamic scan scheduler.
Both kebab-case (`/dynamic-scan/*`) and underscore (`/dynamic_scan/*`) paths
are supported for backward compatibility.

## Start Scan

- **Method**: `POST`
- **Paths**: `/dynamic-scan/start`, `/dynamic_scan/start`
- **Body** (`StartParams`):
  - `interface` *(optional, string)*: network interface to capture packets from
  - `duration` *(optional, int)*: capture duration in seconds
  - `approved_macs` *(optional, list[str])*: allowed MAC addresses
  - `interval` *(optional, int)*: rescan interval in seconds (default 3600)

### Successful Response

```json
{"status": "scheduled"}
```

## Stop Scan

- **Method**: `POST`
- **Paths**: `/dynamic-scan/stop`, `/dynamic_scan/stop`

### Successful Response

```json
{"status": "stopped"}
```

## Get Results

- **Method**: `GET`
- **Paths**: `/dynamic-scan/results`, `/dynamic_scan/results`

### Successful Response

```json
{
  "risk_score": 1,
  "categories": [
    {"name": "protocols", "severity": "high", "issues": ["ftp"]}
  ]
}
```
