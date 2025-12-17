# RTL Network Testing with MSW

This document describes the MSW-based network mocking system for React Testing Library (RTL) tests.

## Overview

RTL tests use **MSW (Mock Service Worker)** to intercept and mock network requests. This system supports two modes:

1. **Live Server Mode** - Proxy requests to a real Django server and cache responses
2. **Cached Mode** - Use previously cached responses for offline testing

## Quick Start

### First-time setup (Live server mode)

Capture responses from a live Django server:

```bash
RTL_LOG_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

This will:
- Start Django server on port 3000
- Run RTL tests
- MSW intercepts all network requests
- Proxy requests to Django server
- Cache responses in `network-testing/logs/network-log-rtl-noi.json`

### Subsequent runs (Cached mode)

Run tests using cached responses (no server needed):

```bash
BASE_SITE=noi BABEL=1 npm run rtltest
```

This will:
- Run RTL tests without starting a server
- MSW loads responses from `network-testing/logs/network-log-rtl-{site}.json`
- Tests run offline using cached data

## Environment Variables

- `RTL_LOG_NETWORK=1` - Enable live server mode with logging
- `BASE_SITE=noi` - Specify which demo site to test (noi, avanti, etc.)
- `BABEL=1` - Required for RTL tests (switches to jsdom environment)

## Architecture

### Components

1. **mswHandlers.ts** (`react/lino_react/react/testSetup/mswHandlers.ts`)
   - Defines MSW request handlers
   - Handles proxying to live server (live mode)
   - Loads and serves cached responses (cached mode)
   - Saves responses to network log files

2. **setupJEST.js** (`react/lino_react/react/testSetup/setupJEST.js`)
   - Starts Django server on port 3000 when `RTL_LOG_NETWORK=1`
   - Waits for server to be ready before running tests

3. **teardownJEST.js** (`react/lino_react/react/testSetup/teardownJEST.js`)
   - Stops Django server after tests complete

4. **setupTests.ts** (`react/lino_react/react/testSetup/setupTests.ts`)
   - Initializes MSW server before tests
   - Sets up MSW handlers
   - Cleans up after tests

### Network Log Format

Cached responses are stored in `network-testing/logs/network-log-rtl-{site}.json`:

```json
{
  "site": "noi",
  "timestamp": "2025-12-10T12:00:00.000Z",
  "requests": [
    {
      "timestamp": "2025-12-10T12:00:01.000Z",
      "request": {
        "method": "GET",
        "url": "http://localhost/api/user",
        "headers": {...},
        "body": null
      },
      "response": {
        "status": 200,
        "statusText": "OK",
        "headers": {...},
        "body": {...}
      }
    }
  ]
}
```

## How It Works

### Live Server Mode (`RTL_LOG_NETWORK=1`)

1. Django server starts on port 3000
2. RTL tests run with MSW enabled
3. When app makes request (e.g., `fetch('/api/user')`):
   - MSW intercepts the request
   - Forwards request to `http://127.0.0.1:3000/api/user`
   - Receives real response from Django
   - Caches response to network log file
   - Returns response to app

4. Tests complete, log file saved, server stops

### Cached Mode (default)

1. No Django server starts
2. RTL tests run with MSW enabled
3. When app makes request (e.g., `fetch('/api/user')`):
   - MSW intercepts the request
   - Looks up request in cached log file
   - Returns cached response to app
   - If no cache found, returns empty response with warning

4. Tests complete (offline, fast)

## Differences from Puppeteer Network Testing

| Feature | Puppeteer (`LOG_NETWORK=1`) | RTL (`RTL_LOG_NETWORK=1`) |
|---------|----------------------------|---------------------------|
| Server port | 3000 | 3000 |
| Log file | `network-log-{site}.json` | `network-log-rtl-{site}.json` |
| Mocking system | `networkMockLoader.js` | MSW |
| Environment | Real browser | jsdom |
| Use case | E2E tests | Unit tests |

## Troubleshooting

### "Cache miss" warnings

If you see warnings like `⚠️ Cache miss: GET /api/user`, run tests with `RTL_LOG_NETWORK=1` to capture that request.

### Server fails to start

Ensure the demo site is prepared:
```bash
python puppeteers/noi/manage.py prep --noinput
```

### Port already in use

The RTL server uses port 3000. If it's in use, kill the process:
```bash
lsof -ti:3000 | xargs kill -9
```

### MSW not working

Ensure MSW is installed:
```bash
npm install
```

Check that `mswHandlers.ts` exists and is properly imported in `setupTests.ts`.

## Best Practices

1. **Always capture fresh responses before CI/deployment**
   ```bash
   RTL_LOG_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
   ```

2. **Commit log files** to version control so other developers can run tests offline

3. **Update logs when API changes** - If backend responses change, recapture

4. **Use different sites** for different test scenarios
   ```bash
   RTL_LOG_NETWORK=1 BASE_SITE=avanti BABEL=1 npm run rtltest
   ```

5. **Verify cached responses** - Occasionally run live mode to ensure cache is current

## Migration from Old System

The old `MOCK_NETWORK` system has been replaced by MSW. Key changes:

- **Old**: `MOCK_NETWORK=1` with manual fetch/XMLHttpRequest mocking
- **New**: MSW with automatic request interception
- **Old**: Used Puppeteer log files (`network-log-{site}.json`)
- **New**: Uses separate RTL log files (`network-log-rtl-{site}.json`)

To migrate:
1. Remove old `MOCK_NETWORK=1` usage
2. Run `RTL_LOG_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest` to generate new cache
3. Tests will automatically use MSW

## See Also

- MSW Documentation: https://mswjs.io/
- React Testing Library: https://testing-library.com/react
- Puppeteer Network Testing: `react/network-testing/README.md`
