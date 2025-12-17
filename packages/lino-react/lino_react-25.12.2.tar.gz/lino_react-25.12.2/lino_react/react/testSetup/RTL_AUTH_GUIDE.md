# RTL Test Authentication Guide

## Overview

The MSW-based RTL testing system automatically handles authentication, including login credentials and session cookies. This guide explains how it works and how to test authenticated features.

## Default Test Credentials

All RTL tests use the demo fixtures created by `manage.py prep`:

```typescript
username: 'robin'
password: '1234'
```

These credentials are defined in `rtlTestHelpers.ts` as `TEST_CREDENTIALS`.

## How Authentication Works

### Live Server Mode (RTL_LOG_NETWORK=1)

When running with `RTL_LOG_NETWORK=1`:

1. **Server Preparation**: Django server is started on port 3000 with demo fixtures
2. **Login Request**: When app makes login POST request, MSW intercepts it
3. **Proxying**: MSW forwards request to Django server with credentials
4. **Session Cookies**: Django response includes `Set-Cookie` headers (sessionid, csrftoken)
5. **Cookie Storage**: MSW captures and stores cookies in the cached response
6. **Subsequent Requests**: All future requests include the session cookies automatically

### Cached Mode (Default)

When running with cached responses:

1. **Login Request**: When app makes login POST request, MSW intercepts it
2. **Cache Lookup**: MSW finds the cached login response
3. **Cookie Replay**: Cached response includes `Set-Cookie` headers
4. **Session Restoration**: Browser receives the same session cookies as the live server provided
5. **Authenticated State**: App continues as if user just logged in to the live server

## Key Implementation Details

### Cookie Handling in MSW Handler

```typescript
// In mswHandlers.ts - Live mode
const response = await fetch(targetUrl, {
    method,
    headers: proxyHeaders,
    body: bodyForProxy,
    credentials: 'include', // ← Critical for cookie handling
});

// Response headers (including Set-Cookie) are preserved
const responseHeaders: Record<string, string> = {};
response.headers.forEach((value, key) => {
    responseHeaders[key] = value;
});
```

### Request Body Handling

The MSW handler properly handles different content types:

```typescript
if (contentType.includes('application/json')) {
    requestBody = await cloned.json();
    bodyForProxy = JSON.stringify(requestBody);
} else if (contentType.includes('application/x-www-form-urlencoded')) {
    const formData = await cloned.text();
    requestBody = formData;
    bodyForProxy = formData;
}
```

## Testing Authenticated Features

### Example 1: Basic Authentication Test

```typescript
import { render, waitFor } from '@testing-library/react';
import { TEST_CREDENTIALS, waitForAppReady, isLoggedIn } from '../../testSetup/rtlTestHelpers';
import { Main } from '../../App';

describe("Authenticated Feature Tests", () => {
    it("should handle login flow", async () => {
        const { container } = render(<Main />);
        
        await waitForAppReady();
        
        // If your app auto-logs in from cached session
        await waitFor(() => {
            expect(isLoggedIn()).toBe(true);
        });
        
        // Now test authenticated features
        // Network requests will include session cookies automatically
    });
});
```

### Example 2: Testing Without Auto-Login

If you need to test the login process itself:

```typescript
it("should perform login", async () => {
    const { container } = render(<Main />);
    
    await waitForAppReady();
    
    // Trigger login in your app's UI
    // MSW will intercept the POST request and either:
    // - Proxy to live server (RTL_LOG_NETWORK=1), or
    // - Return cached login response with session
    
    await waitFor(() => {
        expect(isLoggedIn()).toBe(true);
    });
});
```

## Workflow for Capturing Auth Flows

### First Time Setup (Per Site)

```bash
# 1. Prepare the demo database with test users
cd react/puppeteers/noi
python manage.py prep --noinput

# 2. Run RTL tests with live server to capture auth flow
cd ../../..
RTL_LOG_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

This creates `network-testing/logs/network-log-rtl-noi.json` containing:
- Login POST request with credentials
- Login response with session cookies
- All subsequent authenticated requests

### Subsequent Runs (Offline)

```bash
# Run tests with cached responses (no server needed)
BASE_SITE=noi BABEL=1 npm run rtltest
```

MSW replays the entire auth flow from cache, including cookies.

## Troubleshooting

### "Login not working in cached mode"

**Problem**: Tests fail because user isn't authenticated

**Solutions**:
1. Ensure you ran with `RTL_LOG_NETWORK=1` first to capture login flow
2. Check that `network-log-rtl-{site}.json` exists and contains login requests
3. Verify demo fixtures exist: `python manage.py prep --noinput`

### "Session expired" errors

**Problem**: Cached session cookies have expired

**Solution**: Re-run with `RTL_LOG_NETWORK=1` to capture fresh session

### "CSRF token mismatch"

**Problem**: CSRF token not properly captured/replayed

**Solution**: 
1. Ensure MSW handler preserves all cookies (check `credentials: 'include'`)
2. Re-capture with `RTL_LOG_NETWORK=1`

## Advanced: Custom Authentication

If your app uses different authentication (OAuth, JWT, etc.):

1. **Modify rtlTestHelpers.ts**: Add helpers for your auth method
2. **Update TEST_CREDENTIALS**: Add required tokens/keys
3. **MSW handles it automatically**: Any headers/cookies are captured/replayed

## Files Reference

- `mswHandlers.ts` - MSW request interceptor with cookie handling
- `rtlTestHelpers.ts` - Authentication helper functions
- `setupTests.ts` - MSW initialization
- `network-testing/logs/network-log-rtl-*.json` - Cached auth responses

## Security Note

The cached authentication files contain **test credentials only** (robin/1234). These are demo fixtures and should never contain real user credentials. The cache files can be safely committed to version control as they only work with demo databases.
