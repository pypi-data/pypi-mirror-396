/**
 * Network mock loader for RTL tests
 * Loads network log files and provides mock implementations for fetch and XMLHttpRequest
 */

const fs = require('fs');
const path = require('path');

class NetworkMockLoader {
    constructor(siteName) {
        this.siteName = siteName;
        this.networkLog = null;
        this.requestIndex = new Map(); // Map URL+method to responses
        this.loadNetworkLog();
    }

    loadNetworkLog() {
        const logPath = path.join(__dirname, 'logs', `network-log-${this.siteName}.json`);
        
        try {
            if (fs.existsSync(logPath)) {
                const logData = fs.readFileSync(logPath, 'utf8');
                this.networkLog = JSON.parse(logData);
                this.indexRequests();
                console.log(`📦 Loaded network log for ${this.siteName}: ${this.networkLog.requests.length} requests`);
            } else {
                console.warn(`⚠️  Network log not found: ${logPath}`);
                console.warn(`   Run tests with LOG_NETWORK=1 to generate it first`);
            }
        } catch (error) {
            console.error(`❌ Failed to load network log: ${error.message}`);
        }
    }

    indexRequests() {
        if (!this.networkLog) return;

        // Index requests by URL and method for quick lookup
        this.networkLog.requests.forEach(entry => {
            const key = `${entry.request.method}:${entry.request.url}`;
            
            // Store multiple responses for the same endpoint (for sequential calls)
            if (!this.requestIndex.has(key)) {
                this.requestIndex.set(key, []);
            }
            this.requestIndex.get(key).push(entry);
        });
    }

    findResponse(url, method = 'GET') {
        if (!this.networkLog) return null;

        const key = `${method}:${url}`;
        const entries = this.requestIndex.get(key);
        
        if (entries && entries.length > 0) {
            // Return the first response (for multiple calls, we could cycle through)
            return entries[0].response;
        }

        // Try partial URL match (for dynamic URLs with parameters)
        const urlWithoutQuery = url.split('?')[0];
        for (const [entryKey, entries] of this.requestIndex.entries()) {
            const [entryMethod, entryUrl] = entryKey.split(':', 2);
            const entryUrlWithoutQuery = entryUrl.split('?')[0];
            
            if (entryMethod === method && entryUrlWithoutQuery === urlWithoutQuery) {
                return entries[0].response;
            }
        }

        return null;
    }

    mockFetch() {
        const self = this;
        
        return async function fetch(url, options = {}) {
            const method = options.method || 'GET';
            const response = self.findResponse(url, method);

            if (response) {
                // Create a Response-like object
                return {
                    ok: response.status >= 200 && response.status < 300,
                    status: response.status,
                    statusText: response.statusText || '',
                    headers: new Map(Object.entries(response.headers || {})),
                    json: async () => {
                        if (typeof response.body === 'object') {
                            return response.body;
                        }
                        try {
                            return JSON.parse(response.body);
                        } catch {
                            return response.body;
                        }
                    },
                    text: async () => {
                        if (typeof response.body === 'string') {
                            return response.body;
                        }
                        return JSON.stringify(response.body);
                    },
                    blob: async () => new Blob([JSON.stringify(response.body)]),
                    arrayBuffer: async () => new TextEncoder().encode(JSON.stringify(response.body)).buffer,
                };
            }

            // Fallback: return empty response
            console.warn(`⚠️  No mock response found for: ${method} ${url}`);
            return {
                ok: true,
                status: 200,
                statusText: 'OK',
                headers: new Map(),
                json: async () => ({}),
                text: async () => '{}',
                blob: async () => new Blob(['{}']),
                arrayBuffer: async () => new TextEncoder().encode('{}').buffer,
            };
        };
    }

    mockXMLHttpRequest() {
        const self = this;
        
        return class MockXMLHttpRequest {
            constructor() {
                this.readyState = 0;
                this.status = 0;
                this.statusText = '';
                this.responseText = '';
                this.responseXML = null;
                this.response = null;
                this.responseType = '';
                this.onreadystatechange = null;
                this.onload = null;
                this.onerror = null;
                this.onabort = null;
                this.ontimeout = null;
                this.onprogress = null;
                this.onloadstart = null;
                this.onloadend = null;
                this._method = '';
                this._url = '';
                this._headers = {};
                this._async = true;
            }

            open(method, url, async = true, user, password) {
                this._method = method;
                this._url = url;
                this._async = async;
                this.readyState = 1;
                this._triggerEvent('readystatechange');
            }

            setRequestHeader(name, value) {
                this._headers[name] = value;
            }

            send(data) {
                const response = self.findResponse(this._url, this._method);

                setTimeout(() => {
                    if (response) {
                        this.status = response.status;
                        this.statusText = response.statusText || '';
                        
                        if (typeof response.body === 'object') {
                            this.responseText = JSON.stringify(response.body);
                            this.response = response.body;
                        } else {
                            this.responseText = response.body;
                            try {
                                this.response = JSON.parse(response.body);
                            } catch {
                                this.response = response.body;
                            }
                        }
                    } else {
                        console.warn(`⚠️  No mock response found for: ${this._method} ${this._url}`);
                        this.status = 200;
                        this.statusText = 'OK';
                        this.responseText = '{}';
                        this.response = {};
                    }

                    this.readyState = 4;
                    this._triggerEvent('readystatechange');
                    this._triggerEvent('load');
                    this._triggerEvent('loadend');
                }, 0);
            }

            abort() {
                this._triggerEvent('abort');
            }

            getAllResponseHeaders() {
                return '';
            }

            getResponseHeader(name) {
                return null;
            }

            _triggerEvent(eventName) {
                const handler = this[`on${eventName}`];
                if (handler) {
                    handler.call(this, { type: eventName, target: this });
                }
            }
        };
    }
}

module.exports = NetworkMockLoader;
