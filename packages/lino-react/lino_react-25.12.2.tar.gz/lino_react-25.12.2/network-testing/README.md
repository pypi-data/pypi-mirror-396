# Network Testing - Request Logging & Mocking System

Complete system for capturing network requests from Puppeteer tests and replaying them in React Testing Library tests.

## 📁 Directory Structure

```
network-testing/
├── README.md                    # This file
├── networkLogger.js             # Captures network traffic from Puppeteer tests
├── networkMockLoader.js         # Mocks network requests in RTL tests
├── docs/                        # Documentation
│   ├── NETWORK_LOGGING.md              # Complete documentation
│   ├── NETWORK_LOGGING_QUICKSTART.md   # Quick start guide
│   ├── NETWORK_LOGGING_SUMMARY.md      # Implementation details
│   └── NETWORK_LOGGING_REFERENCE.txt   # Command reference
├── tools/                       # Utility scripts
│   ├── run_with_network_logging.sh     # Run tests with logging
│   ├── demo_network_logging.sh         # Demo logging feature
│   ├── demo_network_workflow.sh        # Complete workflow demo
│   ├── analyze_network_logs.py         # Statistical analysis
│   └── view_network_log.py             # Interactive log viewer
└── logs/                        # Captured network logs (gitignored)
    ├── README.md                       # Logs directory documentation
    ├── network-log-noi.json           # Noi site logs
    └── network-log-*.json             # Other site logs
```

## 🚀 Quick Start

### 1. Capture Network Traffic

Run Puppeteer tests with network logging enabled:

```bash
LOG_NETWORK=1 BASE_SITE=noi npm run itest
```

This creates `network-testing/logs/network-log-noi.json` with all requests/responses.

### 2. Mock RTL Tests

Use captured responses to automatically mock network requests:

```bash
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

All `fetch()` and `XMLHttpRequest` calls will return the logged responses!

### 3. Analyze Results

```bash
# Statistical analysis
python network-testing/tools/analyze_network_logs.py network-testing/logs/network-log-noi.json

# Interactive viewer
python network-testing/tools/view_network_log.py network-testing/logs/network-log-noi.json
```

## 🎯 What It Does

### Network Logging (networkLogger.js)
- Intercepts all network requests during Puppeteer tests
- Captures request details: URL, method, headers, body
- Captures response details: status, headers, body, timing
- Saves everything to JSON for later use

### Network Mocking (networkMockLoader.js)
- Loads captured network logs
- Indexes requests by URL and method
- Provides mock `fetch()` implementation
- Provides mock `XMLHttpRequest` class
- Automatically matches requests to logged responses

## 📊 Use Cases

1. **Debug API Communication** - See exactly what requests are made
2. **Performance Analysis** - Find slow API calls and bottlenecks
3. **Test with Real Data** - RTL tests use actual API responses
4. **Offline Testing** - Run tests without a live server
5. **Documentation** - Generate API usage examples from real tests

## 🛠️ Tools

### Shell Scripts
- **run_with_network_logging.sh** - Convenience script for running tests
- **demo_network_logging.sh** - Demonstrates network logging
- **demo_network_workflow.sh** - Complete capture → mock → analyze workflow

### Python Scripts
- **analyze_network_logs.py** - Statistical analysis (requests by type, status codes, etc.)
- **view_network_log.py** - Interactive viewer with search and filtering

## 📖 Documentation

See `docs/` directory for complete documentation:

- **NETWORK_LOGGING_QUICKSTART.md** - Get started in 5 minutes
- **NETWORK_LOGGING.md** - Complete technical documentation
- **NETWORK_LOGGING_SUMMARY.md** - Implementation details
- **NETWORK_LOGGING_REFERENCE.txt** - Command reference card

## 🔧 Configuration

### Environment Variables

**For Puppeteer Tests (Logging):**
- `LOG_NETWORK=1` - Enable network logging
- `BASE_SITE=noi` - Specify site to test

**For RTL Tests (Mocking):**
- `MOCK_NETWORK=1` - Enable network mocking
- `BASE_SITE=noi` - Specify which site's logs to use
- `BABEL=1` - Enable jsdom environment

### Integration Points

The system integrates automatically with:
- `lino_react/react/testSetup/testEnvironment.js` - Sets up logging
- `lino_react/react/testSetup/setupTests.ts` - Enables mocking
- No changes needed in individual test files!

## 📝 Example Workflow

```bash
# 1. Capture network traffic from Puppeteer tests
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# 2. View what was captured
python network-testing/tools/analyze_network_logs.py \
    network-testing/logs/network-log-noi.json

# 3. Use captured data in RTL tests
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest

# 4. Or run complete demo
cd network-testing/tools
./demo_network_workflow.sh noi
```

## 🎉 Features

- ✅ **Automatic** - No test code changes required
- ✅ **Transparent** - Works with existing tests
- ✅ **Real Data** - Uses actual API responses
- ✅ **Comprehensive** - Captures everything (requests, responses, timing)
- ✅ **Analyzable** - JSON format with analysis tools
- ✅ **Easy** - Enable with environment variables

## 💡 Tips

- Run logging once, mock many times - no need to re-capture for every RTL test run
- Use `demo_network_workflow.sh` to see the complete workflow in action
- Check `logs/README.md` for information about log file structure
- Each site has its own log file that gets overwritten on each run
- Log files can be 1-20MB depending on test suite size

## 🐛 Troubleshooting

**No log file created?**
- Ensure `LOG_NETWORK=1` is set
- Check that Puppeteer tests actually ran (not jsdom mode)

**Mock not working?**
- Ensure log file exists: `ls network-testing/logs/network-log-*.json`
- Verify `MOCK_NETWORK=1` and `BABEL=1` are both set
- Check console for "Network mocking enabled" message

**Need more help?**
- See `docs/NETWORK_LOGGING.md` for detailed documentation
- Check `docs/NETWORK_LOGGING_REFERENCE.txt` for command examples
