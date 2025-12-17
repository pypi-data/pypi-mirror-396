# Network Request Logging for Jest Tests

This setup captures all network requests and responses made during Puppeteer-based tests and saves them to JSON files for analysis.

## Usage

To enable network logging, set the `LOG_NETWORK` environment variable to `1` when running tests:

```bash
# For noi site tests with network logging
LOG_NETWORK=1 BASE_SITE=noi npm run itest

# For avanti site tests with network logging
LOG_NETWORK=1 BASE_SITE=avanti npm run itest
```

## Output

Network logs are saved to the `./network-testing/logs/` directory with filenames in the format:
```
network-log-{site}.json
```

For example:
```
network-testing/logs/network-log-noi.json
network-testing/logs/network-log-avanti.json
```

**Note:** Each test run overwrites the previous log file for that site.

## JSON Structure

The output JSON file contains:

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
        "headers": { ... },
        "postData": null,
        "resourceType": "xhr"
      },
      "response": {
        "timestamp": 245,
        "status": 200,
        "statusText": "OK",
        "headers": { ... },
        "body": { ... },
        "fromCache": false,
        "fromServiceWorker": false
      }
    }
  ]
}
```

### Field Descriptions

#### Metadata
- `testSite`: The site being tested (from `BASE_SITE` env var)
- `timestamp`: ISO timestamp when test completed
- `totalRequests`: Total number of requests captured
- `duration`: Test duration in milliseconds

#### Request
- `id`: Unique request identifier
- `timestamp`: Time since test start (ms)
- `url`: Full request URL
- `method`: HTTP method (GET, POST, etc.)
- `headers`: Request headers object
- `postData`: Request body (for POST/PUT requests)
- `resourceType`: Type of resource (xhr, document, script, stylesheet, etc.)

#### Response
- `timestamp`: Time since test start (ms)
- `status`: HTTP status code
- `statusText`: HTTP status text
- `headers`: Response headers object
- `body`: Response body (parsed JSON for JSON responses, text for others)
- `fromCache`: Whether response came from cache
- `fromServiceWorker`: Whether response came from service worker

## Features

- **Automatic Setup**: Network logging is automatically enabled on all pages created during tests
- **JSON Parsing**: JSON responses are automatically parsed for easier analysis
- **Binary Content Handling**: Binary/non-text content is marked with content type instead of attempting to capture
- **Error Handling**: Failed response captures are logged with error messages
- **Timestamps**: All events include millisecond timestamps relative to test start

## Implementation Details

The network logging is implemented in three parts:

1. **networkLogger.js**: Core logging class that sets up Puppeteer request interception
2. **testEnvironment.js**: Wraps `browser.newPage()` to automatically enable logging on new pages
3. **setupTests.ts**: Saves accumulated logs after all tests complete

The logging uses Puppeteer's request interception API to capture both requests and responses without affecting test execution.

## Analyzing Network Logs

### Quick Analysis

A Python script is provided to analyze the generated logs:

```bash
python analyze_network_logs.py network-logs/network-log-noi-*.json
```

The analysis script provides:
- Request counts by HTTP method
- Request counts by resource type
- Response status code distribution
- List of API endpoint calls
- Identification of slow requests (>1 second)
- List of failed requests (4xx/5xx status codes)

### Interactive Viewer

For detailed inspection of individual requests:

```bash
python network-testing/tools/view_network_log.py network-testing/logs/network-log-noi.json
```

The interactive viewer allows you to:
- Browse all requests by index
- Filter by API requests only
- View failed requests
- Find slow requests
- Search for specific URLs
- View full request/response details including headers and body

## Convenience Scripts

### run_with_network_logging.sh

A bash script that combines test preparation and execution with network logging:

```bash
# Run with site preparation
./run_with_network_logging.sh noi

# Skip preparation step
./run_with_network_logging.sh noi skipprep

# Use different site
./run_with_network_logging.sh avanti
```

## Network Mocking for RTL Tests

The captured network logs can be used to mock network requests in React Testing Library (RTL) tests:

### Step 1: Capture Network Logs
First, run Puppeteer tests with network logging to capture real responses:
```bash
LOG_NETWORK=1 BASE_SITE=noi npm run itest
```

This creates `network-logs/network-log-noi.json` with all captured requests/responses.

### Step 2: Run RTL Tests with Mocking
Then run RTL tests using the captured responses:
```bash
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

The `MOCK_NETWORK=1` flag enables automatic mocking of:
- `fetch()` API
- `XMLHttpRequest` objects

All network requests will return the responses captured from the Puppeteer test run, allowing RTL tests to work with real data without running a live server.

### How It Works
- `networkMockLoader.js` indexes all requests by URL and method
- When RTL code makes a `fetch()` call, it's intercepted and matched against logged responses
- The mock returns the exact response captured during Puppeteer tests
- URL matching supports both exact matches and partial matches (for query parameters)

## Notes

- Network logging only works with Puppeteer tests (not jsdom/BABEL=1 mode)
- Each test run overwrites the previous log file for that site
- Large response bodies are captured in full - monitor disk space for long test runs
- Binary content (images, PDFs, etc.) is not captured, only metadata
- Network mocking is transparent - no test code changes needed
