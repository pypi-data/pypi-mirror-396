# Network Request Logging - Quick Start Guide

## What This Does

Captures ALL network requests and responses made during your Jest/Puppeteer tests and saves them as JSON files for detailed analysis.

## Quick Usage

```bash
# Option 1: Use the convenience script
./run_with_network_logging.sh noi

# Option 2: Set LOG_NETWORK=1 manually
LOG_NETWORK=1 BASE_SITE=noi npm run itest
```

## Output Location

```
network-testing/logs/network-log-noi.json
network-testing/logs/network-log-avanti.json
```

Note: Each site has its own log file that gets overwritten on each test run.

## Quick Analysis

```bash
# Analyze the logs
python analyze_network_logs.py network-logs/*.json
```

This will show you:
- Total request counts
- Request breakdown by method (GET, POST, etc.)
- API endpoint calls
- Slow requests (>1 second)
- Failed requests (errors)

## Full Documentation

- [NETWORK_LOGGING.md](./NETWORK_LOGGING.md) - Complete documentation
- [NETWORK_LOGGING_SUMMARY.md](./NETWORK_LOGGING_SUMMARY.md) - Implementation details
- [NETWORK_LOGGING_REFERENCE.txt](./NETWORK_LOGGING_REFERENCE.txt) - Command reference

## Network Mocking for RTL Tests

You can use the captured logs to mock network requests in React Testing Library tests:

```bash
# Step 1: Capture responses from Puppeteer tests
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# Step 2: Use captured responses in RTL tests
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

This automatically mocks `fetch()` and `XMLHttpRequest` with real responses from your Puppeteer tests!

## Complete Workflow Demo

```bash
# Run the full workflow: capture + mock + analyze
./demo_network_workflow.sh noi
```

## Files Structure

```
network-testing/
├── networkLogger.js              # Core logging implementation
├── networkMockLoader.js          # Network mocking for RTL tests
├── docs/                         # All documentation
├── tools/                        # Analysis and demo scripts
└── logs/                         # Where logs are saved (gitignored)
```
