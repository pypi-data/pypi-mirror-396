# Network Logs Directory

This directory stores captured network request/response logs from Jest/Puppeteer tests.

## File Format

Each site has its own log file:
- `network-log-noi.json` - Noi site requests
- `network-log-avanti.json` - Avanti site requests
- `network-log-*.json` - Other site requests

**Note:** Each test run overwrites the previous log for that site.

## How to Generate

Run Puppeteer tests with network logging enabled:

```bash
LOG_NETWORK=1 BASE_SITE=noi npm run itest
```

## How to Use

### 1. Analyze Captured Traffic
```bash
# Statistical analysis
python ../tools/analyze_network_logs.py network-log-noi.json

# Interactive viewer
python ../tools/view_network_log.py network-log-noi.json
```

### 2. Mock RTL Tests
Use captured responses to automatically mock network requests in React Testing Library tests:

```bash
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

All `fetch()` and `XMLHttpRequest` calls will return the logged responses!

## File Structure

Each log file contains:

```json
{
  "metadata": {
    "testSite": "noi",
    "timestamp": "2025-12-09T14:30:45.123Z",
    "totalRequests": 42,
    "duration": 15234
  },
  "requests": [
    {
      "request": {
        "url": "http://127.0.0.1:3000/api/...",
        "method": "GET",
        "headers": {...},
        "body": "...",
        "timestamp": 123
      },
      "response": {
        "status": 200,
        "headers": {...},
        "body": {...},
        "timestamp": 245
      }
    }
  ]
}
```

## Typical File Sizes

- Small test suite: ~100 KB - 1 MB
- Medium test suite: 1 MB - 5 MB
- Large test suite: 5 MB - 20 MB

## Maintenance

These files are generated automatically and can be safely deleted. They will be recreated on the next test run with `LOG_NETWORK=1`.

To clean up old logs:
```bash
rm network-logs/*.json
```

## See Also

- `../docs/NETWORK_LOGGING_QUICKSTART.md` - Quick start guide
- `../docs/NETWORK_LOGGING.md` - Complete documentation
- `../docs/NETWORK_LOGGING_REFERENCE.txt` - Command reference
- `../README.md` - Main network-testing documentation
