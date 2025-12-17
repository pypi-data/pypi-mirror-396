# Network Request Logging & Mocking

> **All network testing tools have been organized into the `network-testing/` directory**

## Quick Start

```bash
# Capture network traffic from Puppeteer tests
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# Use captured responses in RTL tests  
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

## Documentation

See **`network-testing/README.md`** for complete documentation.

Quick links:
- [`network-testing/README.md`](./network-testing/README.md) - Main documentation
- [`network-testing/docs/NETWORK_LOGGING_QUICKSTART.md`](./network-testing/docs/NETWORK_LOGGING_QUICKSTART.md) - Quick start guide
- [`network-testing/docs/NETWORK_LOGGING_REFERENCE.txt`](./network-testing/docs/NETWORK_LOGGING_REFERENCE.txt) - Command reference

## Tools & Scripts

All tools are in `network-testing/tools/`:
- `run_with_network_logging.sh` - Run tests with logging
- `demo_network_workflow.sh` - Complete workflow demo
- `analyze_network_logs.py` - Statistical analysis
- `view_network_log.py` - Interactive viewer

## Output Location

Logs are saved in: **`network-testing/logs/`**
- `network-log-noi.json`
- `network-log-avanti.json`
- etc.

## Example Workflow

```bash
# 1. Capture (generates network-testing/logs/network-log-noi.json)
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# 2. Analyze
python network-testing/tools/analyze_network_logs.py \
    network-testing/logs/network-log-noi.json

# 3. Mock in RTL tests
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest

# Or run complete demo
network-testing/tools/demo_network_workflow.sh noi
```
