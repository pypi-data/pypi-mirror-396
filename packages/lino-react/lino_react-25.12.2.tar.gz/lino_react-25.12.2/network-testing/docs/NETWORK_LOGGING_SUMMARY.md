# Network Request Logging - Complete Setup Summary

## ✅ What Was Implemented

A complete network request/response logging system for Jest/Puppeteer tests that:
- Automatically captures ALL network traffic during test execution
- Saves detailed JSON logs with request/response data
- Provides analysis and viewing tools

## 📁 Files Created/Modified

### Core Implementation
- **`lino_react/react/testSetup/networkLogger.js`** - Main logging class with Puppeteer request interception
- **`lino_react/react/testSetup/networkMockLoader.js`** - Network mocking system for RTL tests
- **`lino_react/react/testSetup/testEnvironment.js`** - Modified to wrap `newPage()` and enable logging
- **`lino_react/react/testSetup/setupTests.ts`** - Modified to save logs and enable network mocking
- **`lino_react/react/components/__tests__/noi/RTLTests.tsx`** - Updated with mocking documentation
- **`.gitignore`** - Updated to ignore `network-logs/` directory

### User Scripts & Tools
- **`run_with_network_logging.sh`** - Convenience script to run tests with logging
- **`demo_network_workflow.sh`** - Complete workflow demo (capture + mock + analyze)
- **`demo_network_logging.sh`** - Demo script showing network logging
- **`analyze_network_logs.py`** - Statistical analysis of captured logs
- **`view_network_log.py`** - Interactive viewer for detailed request inspection

### Documentation
- **`NETWORK_LOGGING.md`** - Complete technical documentation
- **`NETWORK_LOGGING_QUICKSTART.md`** - Quick start guide
- **`NETWORK_LOGGING_SUMMARY.md`** - This file

## 🚀 How to Use

### Network Logging (Capture Responses)
```bash
# Option 1: Convenience Script
./run_with_network_logging.sh noi

# Option 2: Manual Command
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# Option 3: Demo
./demo_network_logging.sh
```

### Network Mocking (Use Captured Responses in RTL)
```bash
# Step 1: Capture from Puppeteer tests
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# Step 2: Mock in RTL tests
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest

# Complete workflow demo
./demo_network_workflow.sh noi
```

## 📊 Analyzing Results

### Quick Statistical Analysis
```bash
python analyze_network_logs.py network-logs/*.json
```
Shows: request counts, API endpoints, slow requests, failed requests

### Interactive Detailed View
```bash
python view_network_log.py network-logs/network-log-noi-2025-12-09.json
```
Browse individual requests, search, filter by type

### Manual Inspection
```bash
# View with jq
jq '.' network-logs/network-log-noi-*.json | less

# View in VS Code
code network-logs/network-log-noi-*.json
```

## 📦 Output Format

Log files are saved as `network-logs/network-log-{site}.json` (e.g., `network-log-noi.json`).

Each test run overwrites the previous log for that site.

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
        "id": "req-0",
        "timestamp": 123,
        "url": "http://127.0.0.1:3000/api/...",
        "method": "GET",
        "headers": {...},
        "postData": null,
        "resourceType": "xhr"
      },
      "response": {
        "timestamp": 245,
        "status": 200,
        "headers": {...},
        "body": {...}
      }
    }
  ]
}
```

## 🎯 Use Cases

1. **Debug API Communication**
   - See exactly what requests are made
   - Inspect request/response payloads
   - Identify missing or incorrect parameters

2. **Performance Analysis**
   - Find slow API calls
   - Identify unnecessary requests
   - Optimize request patterns

3. **Testing & Validation**
   - Verify correct API endpoints are called
   - Validate request parameters
   - Check response data structure

4. **RTL Test Mocking**
   - Automatically mock network requests in RTL tests
   - Use real response data captured from Puppeteer tests
   - Keep test data synchronized with actual API responses
   - No manual mocking required

5. **Documentation**
   - Generate API usage examples from real tests
   - Document actual request/response flows
   - Create integration test scenarios

## ⚙️ Configuration

The system is controlled by environment variables:

**Network Logging (Puppeteer Tests):**
- **`LOG_NETWORK=1`** - Enable network logging
- **`BASE_SITE=noi`** - Specify which site to test

**Network Mocking (RTL Tests):**
- **`MOCK_NETWORK=1`** - Enable network mocking from logged responses
- **`BASE_SITE=noi`** - Specify which site's log to use
- **`BABEL=1`** - Enable jsdom environment (standard for RTL)

No code changes needed in test files - everything is transparent!

## 🔍 Technical Details

### How It Works
1. `testEnvironment.js` wraps `browser.newPage()` to automatically call `networkLogger.setupPage()`
2. `networkLogger.js` uses Puppeteer's request interception to capture traffic
3. Both requests and responses are stored in memory during test execution
4. `setupTests.ts` saves the accumulated log to JSON after all tests complete

### What's Captured
- ✅ All HTTP/HTTPS requests from the browser
- ✅ Request headers, method, URL, body
- ✅ Response status, headers, body (text/JSON)
- ✅ Timing information (timestamps, duration)
- ✅ Resource types (xhr, document, script, etc.)
- ❌ Binary content (images, PDFs) - only metadata captured

### Performance Impact
- Minimal - logging runs asynchronously
- No test modification required
- Tests run at normal speed
- Disk space: ~1-5MB per test run (varies by site)

## 🧪 Testing the Setup

To verify everything works:

```bash
# Run demo (includes prep + tests + analysis)
./demo_network_logging.sh

# Or manually
LOG_NETWORK=1 BASE_SITE=noi npm run itest
ls -lh network-logs/
python analyze_network_logs.py network-logs/*.json
```

You should see:
- Console messages about network logging being enabled
- A new JSON file in `network-logs/`
- Analysis output showing request statistics

## 🐛 Troubleshooting

**No log file created?**
- Ensure `LOG_NETWORK=1` is set
- Check that tests actually ran (not jsdom/BABEL=1 mode)
- Verify `network-logs/` directory exists

**Empty or incomplete log?**
- Some tests may not create pages - check test output
- Ensure tests completed (didn't crash early)

**"Request interception already enabled" error?**
- This shouldn't happen, but if it does, the test file may be setting up interception manually
- Can be safely ignored if logs are still captured

## 📚 Additional Resources

- See `NETWORK_LOGGING.md` for detailed JSON structure
- See `NETWORK_LOGGING_QUICKSTART.md` for quick reference
- Check test output for console messages about logging status

## 🎉 Summary

You now have a complete network logging and mocking system that:
- ✅ Captures all network traffic from Puppeteer tests
- ✅ Saves to simple, site-based JSON files
- ✅ Automatically mocks network requests in RTL tests
- ✅ Uses real response data for accurate testing
- ✅ Provides analysis and viewing tools
- ✅ Requires no test code modifications
- ✅ Easy to enable/disable via environment variables

**Workflow:**
1. Capture: `LOG_NETWORK=1 BASE_SITE=noi npm run itest`
2. Mock RTL: `MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest`
3. Analyze: `python analyze_network_logs.py network-logs/network-log-noi.json`
