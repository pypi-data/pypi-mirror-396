/**
 * MSW (Mock Service Worker) handlers for RTL tests
 * 
 * This module provides two modes:
 * 1. RTL_LOG_NETWORK=1: Proxy requests to live Django server and cache responses
 * 2. RTL_LOG_NETWORK not set: Load cached responses from network-testing/logs
 * 
 * AUTHENTICATION HANDLING:
 * - Live mode: Session cookies from login are automatically captured and stored
 * - Cached mode: Session cookies are replayed from cached responses
 * - Credentials: Tests use demo fixtures (username: 'robin', password: '1234')
 * - The Django server must be prepared with `manage.py prep --noinput` for login to work
 */

// Import from main msw package (BroadcastChannel polyfill provided in setupTests.ts)
import { http, HttpResponse } from 'msw';
import * as fs from 'fs';
import * as path from 'path';

const NETWORK_LOG_DIR = path.join(__dirname, '../../../network-testing/logs');
const RTL_LOG_NETWORK = process.env.RTL_LOG_NETWORK === '1';
const BASE_SITE = process.env.BASE_SITE || 'noi';
const SERVER_URL = process.env.RTL_SERVER_URL || 'http://127.0.0.1:3001';

interface NetworkLogEntry {
    timestamp: string;
    request: {
        method: string;
        url: string;
        headers?: Record<string, string>;
        body?: any;
    };
    response: {
        status: number;
        statusText?: string;
        headers?: Record<string, string>;
        body?: any;
    };
}

interface NetworkLog {
    site: string;
    timestamp: string;
    requests: NetworkLogEntry[];
}

class RTLNetworkLogger {
    private log: NetworkLog;
    private logPath: string;
    private requestMap: Map<string, NetworkLogEntry>;

    constructor(siteName: string) {
        this.logPath = path.join(NETWORK_LOG_DIR, `network-log-rtl-${siteName}.json`);
        this.requestMap = new Map();
        
        if (RTL_LOG_NETWORK) {
            // Initialize new log for recording
            this.log = {
                site: siteName,
                timestamp: new Date().toISOString(),
                requests: []
            };
            console.log(`📝 RTL Network logging enabled - will save to: ${this.logPath}`);
        } else {
            // Load existing log for playback
            this.loadLog();
        }
    }

    private loadLog() {
        try {
            if (fs.existsSync(this.logPath)) {
                const data = fs.readFileSync(this.logPath, 'utf8');
                this.log = JSON.parse(data);
                this.indexRequests();
                console.log(`📦 Loaded RTL network log: ${this.log.requests.length} requests`);
            } else {
                console.warn(`⚠️  RTL network log not found: ${this.logPath}`);
                console.warn(`   Run tests with RTL_LOG_NETWORK=1 to generate it`);
                this.log = {
                    site: BASE_SITE,
                    timestamp: new Date().toISOString(),
                    requests: []
                };
            }
        } catch (error) {
            console.error(`❌ Failed to load RTL network log:`, error);
            this.log = {
                site: BASE_SITE,
                timestamp: new Date().toISOString(),
                requests: []
            };
        }
    }

    private indexRequests() {
        // Index requests by method:url for quick lookup
        this.log.requests.forEach(entry => {
            const key = this.makeKey(entry.request.method, entry.request.url);
            
            // For duplicate keys, keep first occurrence (could be enhanced to track all)
            if (!this.requestMap.has(key)) {
                this.requestMap.set(key, entry);
            }
        });
    }

    private makeKey(method: string, url: string): string {
        // Normalize URL to handle query parameter variations
        const urlObj = new URL(url, 'http://dummy');
        const pathAndQuery = urlObj.pathname + urlObj.search;
        return `${method.toUpperCase()}:${pathAndQuery}`;
    }

    async logRequest(method: string, url: string, requestHeaders: Headers, requestBody: any, response: Response) {
        const responseBody = await this.extractBody(response.clone());
        
        const entry: NetworkLogEntry = {
            timestamp: new Date().toISOString(),
            request: {
                method: method.toUpperCase(),
                url: url,
                headers: this.headersToObject(requestHeaders),
                body: requestBody
            },
            response: {
                status: response.status,
                statusText: response.statusText,
                headers: this.headersToObject(response.headers),
                body: responseBody
            }
        };

        this.log.requests.push(entry);
        this.saveLog();
    }

    private headersToObject(headers: Headers): Record<string, string> {
        const obj: Record<string, string> = {};
        headers.forEach((value, key) => {
            obj[key] = value;
        });
        return obj;
    }

    private async extractBody(response: Response): Promise<any> {
        const contentType = response.headers.get('content-type') || '';
        
        if (contentType.includes('application/json')) {
            try {
                return await response.json();
            } catch {
                return await response.text();
            }
        } else {
            return await response.text();
        }
    }

    private saveLog() {
        try {
            // Ensure directory exists
            if (!fs.existsSync(NETWORK_LOG_DIR)) {
                fs.mkdirSync(NETWORK_LOG_DIR, { recursive: true });
            }
            
            fs.writeFileSync(this.logPath, JSON.stringify(this.log, null, 2), 'utf8');
        } catch (error) {
            console.error(`❌ Failed to save RTL network log:`, error);
        }
    }

    findCachedResponse(method: string, url: string): NetworkLogEntry | null {
        const key = this.makeKey(method, url);
        const entry = this.requestMap.get(key);
        
        if (entry) {
            return entry;
        }

        // Try partial match (for dynamic URLs)
        const normalizedUrl = new URL(url, 'http://dummy');
        const pathOnly = normalizedUrl.pathname;
        
        for (const [entryKey, entry] of this.requestMap.entries()) {
            const [entryMethod, entryPath] = entryKey.split(':', 2);
            const entryPathOnly = entryPath.split('?')[0];
            
            if (entryMethod === method.toUpperCase() && entryPathOnly === pathOnly) {
                console.log(`✅ Partial match found for ${method} ${url}`);
                return entry;
            }
        }

        return null;
    }
}

// Create logger instance
const logger = new RTLNetworkLogger(BASE_SITE);

/**
 * Create MSW handlers for all HTTP requests
 */
export const handlers = [
    // Catch-all handler for all HTTP methods
    http.all(/.*/, async ({ request }) => {
        const method = request.method;
        const url = request.url;

        // Extract request body if present
        let requestBody = null;
        let bodyForProxy = null;
        if (request.body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            try {
                const cloned = request.clone();
                const contentType = request.headers.get('content-type') || '';
                
                if (contentType.includes('application/json')) {
                    requestBody = await cloned.json();
                    bodyForProxy = JSON.stringify(requestBody);
                } else if (contentType.includes('application/x-www-form-urlencoded')) {
                    const formData = await cloned.text();
                    requestBody = formData;
                    bodyForProxy = formData;
                } else {
                    requestBody = await cloned.text();
                    bodyForProxy = requestBody;
                }
            } catch {
                // Body not readable
            }
        }

        if (RTL_LOG_NETWORK) {
            // Mode 1: Proxy to live server and log response
            console.log(`🔄 Proxying: ${method} ${url}`);
            
            try {
                // Convert relative URL to absolute for the Django server
                const targetUrl = url.startsWith('http') 
                    ? url.replace(/^https?:\/\/[^/]+/, SERVER_URL)
                    : `${SERVER_URL}${url}`;

                // Prepare headers for proxy request
                const proxyHeaders: Record<string, string> = {};
                request.headers.forEach((value, key) => {
                    // Skip host header to avoid conflicts
                    if (key.toLowerCase() !== 'host') {
                        proxyHeaders[key] = value;
                    }
                });

                // Make actual request to Django server
                const response = await fetch(targetUrl, {
                    method,
                    headers: proxyHeaders,
                    body: bodyForProxy,
                    credentials: 'include', // Important for cookies/session
                });

                // Log the request/response (including cookies)
                await logger.logRequest(method, url, request.headers, requestBody, response.clone());

                // Extract response body
                const responseBody = await response.clone().text();
                
                // Prepare response headers (including Set-Cookie)
                const responseHeaders: Record<string, string> = {};
                response.headers.forEach((value, key) => {
                    responseHeaders[key] = value;
                });

                return new HttpResponse(responseBody, {
                    status: response.status,
                    statusText: response.statusText,
                    headers: responseHeaders,
                });
            } catch (error) {
                console.error(`❌ Proxy error for ${method} ${url}:`, error);
                return new HttpResponse('{"error": "Proxy failed"}', { 
                    status: 500,
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        } else {
            // Mode 2: Load from cache
            const cached = logger.findCachedResponse(method, url);
            
            if (cached) {
                console.log(`✅ Cache hit: ${method} ${url}`);
                
                const body = typeof cached.response.body === 'object'
                    ? JSON.stringify(cached.response.body)
                    : cached.response.body;

                return new HttpResponse(body, {
                    status: cached.response.status,
                    statusText: cached.response.statusText || 'OK',
                    headers: cached.response.headers || {},
                });
            } else {
                console.warn(`⚠️  Cache miss: ${method} ${url}`);
                console.warn(`   Response will be empty - run with RTL_LOG_NETWORK=1 to capture`);
                
                return new HttpResponse('{}', {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        }
    }),
];

export { logger as rtlNetworkLogger };
