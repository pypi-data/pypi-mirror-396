import React from 'react';
import {render, screen, waitFor} from '@testing-library/react';
import { Main } from '../../App';

/**
 * RTL Tests with MSW Network Mocking
 * 
 * Two modes available:
 * 
 * 1. Live server with logging (RTL_LOG_NETWORK=1):
 *    RTL_LOG_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
 *    - Starts Django server on port 3000 (must run `manage.py prep` first)
 *    - MSW proxies all requests to live server
 *    - Responses are cached in network-testing/logs/network-log-rtl-{site}.json
 *    - Session cookies from login are automatically captured
 * 
 * 2. Cached responses (default):
 *    BASE_SITE=noi BABEL=1 npm run rtltest
 *    - MSW loads responses from network-testing/logs/network-log-rtl-{site}.json
 *    - No server needed, tests run offline
 *    - Session cookies are replayed from cache
 * 
 * AUTHENTICATION:
 * - Demo credentials: username='robin', password='1234'
 * - These are created by `manage.py prep --noinput`
 * - Login requests/responses are captured/replayed like any other request
 * - See rtlTestHelpers.ts for authentication helper functions
 * 
 * The old MOCK_NETWORK system has been replaced by MSW for better reliability.
 */

describe("Test render", () => {
    it("render App", async () => {
        // Suppress CSS parsing warnings from jsdom (expected behavior)
        const originalConsoleError = console.error;
        console.error = (...args) => {
            const errorStr = String(args[0]);
            if (!errorStr.includes('Could not parse CSS stylesheet')) {
                originalConsoleError(...args);
            }
        };

        try {
            const { container } = render(<Main />);
            
            // Wait for App to be available on window
            await waitFor(() => {
                expect(window.App).toBeDefined();
                return window.App && window.App.URLContext;
            }, { timeout: 2000 });
            
            // Wait for the app to render content (Main component initially returns null until modules load)
            await waitFor(() => {
                expect(container.firstChild).toBeTruthy();
            }, { timeout: 5000 });
            
            // Verify some app element is rendered
            const progressBar = container.querySelector('.p-progressbar');
            const tempIframe = container.querySelector('#temp');
            expect(progressBar || tempIframe).toBeTruthy();
        } catch (error) {
            // The App.prepare() method may throw an intentional error in production
            // This is expected behavior, so we only fail if it's a different error
            if (typeof error === 'string' && error.includes('Intentionally raised')) {
                // This is the expected error, test passes
                return;
            }
            // Unexpected error, rethrow
            throw error;
        } finally {
            console.error = originalConsoleError;
        }
    });
});