/**
 * Helper utilities for RTL tests
 * Provides common test patterns and authentication helpers
 */

import { waitFor } from '@testing-library/react';

/**
 * Default test credentials
 * These match the demo fixtures created by manage.py prep
 */
export const TEST_CREDENTIALS = {
    username: 'robin',
    password: '1234',
};

/**
 * Wait for window.App to be initialized
 */
export async function waitForAppReady(timeout = 5000) {
    await waitFor(() => {
        expect(window.App).toBeDefined();
        expect(window.App.URLContext).toBeDefined();
    }, { timeout });
}

/**
 * Check if user is logged in
 */
export function isLoggedIn(): boolean {
    return window.App?.state?.user_settings?.logged_in || false;
}

/**
 * Perform login action (for tests that need authenticated state)
 * 
 * Note: When using RTL_LOG_NETWORK=1, login requests are proxied to the live server
 * and the session cookies are automatically captured and cached. When running with
 * cached responses, the login response (including session) is replayed from cache.
 * 
 * @param credentials - Login credentials (defaults to TEST_CREDENTIALS)
 */
export async function performLogin(credentials = TEST_CREDENTIALS) {
    if (isLoggedIn()) {
        return; // Already logged in
    }

    // This is a placeholder - actual implementation depends on how your app handles login
    // The MSW system will intercept the POST request and either:
    // 1. Proxy it to the live server (RTL_LOG_NETWORK=1), or
    // 2. Return the cached login response with session cookies
    
    // Example login flow (adjust based on your actual implementation):
    // const response = await fetch('/api/auth/sign_in', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(credentials),
    //     credentials: 'include', // Important for cookies
    // });
    
    // Wait for login to complete
    await waitFor(() => {
        expect(isLoggedIn()).toBe(true);
    }, { timeout: 3000 });
}

/**
 * Common test setup that waits for app initialization
 */
export async function setupTest() {
    await waitForAppReady();
}

/**
 * Clean up after tests
 */
export function cleanupTest() {
    // Add any cleanup logic here if needed
}
