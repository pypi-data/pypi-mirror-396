# Network Testing Directory Structure

```
network-testing/
│
├── README.md                           ← START HERE - Main documentation
├── ORGANIZATION_SUMMARY.md             ← How this directory is organized
│
├── networkLogger.js                    ← Core: Puppeteer request capture
├── networkMockLoader.js                ← Core: RTL request mocking
│
├── docs/                               ← All documentation
│   ├── NETWORK_LOGGING.md                     Complete technical documentation
│   ├── NETWORK_LOGGING_QUICKSTART.md          5-minute quick start guide
│   ├── NETWORK_LOGGING_SUMMARY.md             Implementation details
│   └── NETWORK_LOGGING_REFERENCE.txt          Command reference card (quick copy/paste)
│
├── tools/                              ← Utility scripts
│   ├── run_with_network_logging.sh            Run Puppeteer tests + capture
│   ├── demo_network_logging.sh                Demo the logging feature
│   ├── demo_network_workflow.sh               Demo complete workflow (capture→mock)
│   ├── analyze_network_logs.py                Statistical analysis of logs
│   └── view_network_log.py                    Interactive log viewer
│
└── logs/                               ← Output directory (*.json files gitignored)
    ├── README.md                              About the log files
    ├── network-log-noi.json                   Noi site captured requests
    ├── network-log-avanti.json                Avanti site captured requests
    └── network-log-*.json                     Other sites...
```

## Quick Navigation

**New to this system?**
→ Read [`README.md`](./README.md)

**Want to start quickly?**
→ Read [`docs/NETWORK_LOGGING_QUICKSTART.md`](./docs/NETWORK_LOGGING_QUICKSTART.md)

**Need command examples?**
→ See [`docs/NETWORK_LOGGING_REFERENCE.txt`](./docs/NETWORK_LOGGING_REFERENCE.txt)

**Want all the details?**
→ Read [`docs/NETWORK_LOGGING.md`](./docs/NETWORK_LOGGING.md)

**Ready to try it?**
→ Run `tools/demo_network_workflow.sh noi`

**Want to analyze logs?**
→ Use `tools/analyze_network_logs.py logs/network-log-noi.json`

**Want to browse logs interactively?**
→ Use `tools/view_network_log.py logs/network-log-noi.json`

## File Purposes

### Core Implementation
- **networkLogger.js** - Intercepts network requests during Puppeteer tests, saves to JSON
- **networkMockLoader.js** - Loads JSON logs, provides mock fetch/XMLHttpRequest for RTL tests

### Documentation
- **README.md** - Main entry point with overview, quick start, examples
- **docs/NETWORK_LOGGING.md** - Complete reference: features, JSON format, troubleshooting
- **docs/NETWORK_LOGGING_QUICKSTART.md** - Minimal steps to get started fast
- **docs/NETWORK_LOGGING_SUMMARY.md** - Technical implementation details
- **docs/NETWORK_LOGGING_REFERENCE.txt** - Command cheat sheet
- **ORGANIZATION_SUMMARY.md** - How this directory was organized
- **INDEX.md** - This file (navigation guide)

### Tools
- **tools/run_with_network_logging.sh** - Wrapper to run tests with `LOG_NETWORK=1`
- **tools/demo_network_logging.sh** - Runs tests and shows analysis
- **tools/demo_network_workflow.sh** - Complete demo: capture → analyze → mock RTL
- **tools/analyze_network_logs.py** - CLI tool for statistical analysis
- **tools/view_network_log.py** - CLI tool for interactive browsing

### Logs
- **logs/README.md** - Explains log file structure and usage
- **logs/*.json** - Captured request/response data (gitignored, auto-generated)

## Usage Patterns

### Pattern 1: Capture & Analyze
```bash
LOG_NETWORK=1 BASE_SITE=noi npm run itest
python network-testing/tools/analyze_network_logs.py network-testing/logs/network-log-noi.json
```

### Pattern 2: Capture & Mock RTL
```bash
LOG_NETWORK=1 BASE_SITE=noi npm run itest
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

### Pattern 3: Complete Workflow Demo
```bash
network-testing/tools/demo_network_workflow.sh noi
```

## Integration Points

This system integrates with:
- `lino_react/react/testSetup/testEnvironment.js` - Sets up network logging
- `lino_react/react/testSetup/setupTests.ts` - Enables network mocking
- `.gitignore` - Ignores `network-testing/logs/*.json`

No changes needed in test files themselves!
