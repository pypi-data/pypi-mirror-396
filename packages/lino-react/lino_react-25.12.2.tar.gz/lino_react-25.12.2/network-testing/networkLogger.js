const {writeFile, mkdir} = require('fs').promises;
const path = require('path');

class NetworkLogger {
    constructor(outputDir = './network-testing/logs') {
        this.outputDir = outputDir;
        this.requests = [];
        this.startTime = Date.now();
    }

    async setupPage(page) {
        // Enable request interception
        await page.setRequestInterception(true);

        // Track requests
        page.on('request', (request) => {
            const requestData = {
                id: request._requestId || `req-${this.requests.length}`,
                timestamp: Date.now() - this.startTime,
                url: request.url(),
                method: request.method(),
                headers: request.headers(),
                postData: request.postData(),
                resourceType: request.resourceType(),
            };

            this.requests.push({
                request: requestData,
                response: null,
            });

            // Continue the request
            request.continue();
        });

        // Track responses
        page.on('response', async (response) => {
            const request = response.request();
            const requestId = request._requestId || `req-${this.requests.findIndex(r => r.request.url === request.url())}`;
            
            // Find the matching request
            const entry = this.requests.find(r => 
                r.request.id === requestId || 
                (r.request.url === request.url() && !r.response)
            );

            if (entry) {
                try {
                    let responseBody = null;
                    const contentType = response.headers()['content-type'] || '';
                    
                    // Only capture text-based responses
                    if (contentType.includes('application/json') || 
                        contentType.includes('text/') || 
                        contentType.includes('application/javascript')) {
                        try {
                            responseBody = await response.text();
                            // Try to parse JSON for better formatting
                            if (contentType.includes('application/json')) {
                                try {
                                    responseBody = JSON.parse(responseBody);
                                } catch (e) {
                                    // Keep as text if JSON parsing fails
                                }
                            }
                        } catch (e) {
                            responseBody = `[Failed to read response body: ${e.message}]`;
                        }
                    } else {
                        responseBody = `[Binary or non-text content: ${contentType}]`;
                    }

                    entry.response = {
                        timestamp: Date.now() - this.startTime,
                        status: response.status(),
                        statusText: response.statusText(),
                        headers: response.headers(),
                        body: responseBody,
                        fromCache: response.fromCache(),
                        fromServiceWorker: response.fromServiceWorker(),
                    };
                } catch (error) {
                    entry.response = {
                        error: `Failed to capture response: ${error.message}`,
                        timestamp: Date.now() - this.startTime,
                        status: response.status(),
                    };
                }
            }
        });
    }

    async saveToFile(filename) {
        await mkdir(this.outputDir, { recursive: true });
        const filePath = path.join(this.outputDir, filename);
        
        const output = {
            metadata: {
                testSite: process.env.BASE_SITE || 'unknown',
                timestamp: new Date().toISOString(),
                totalRequests: this.requests.length,
                duration: Date.now() - this.startTime,
            },
            requests: this.requests,
        };

        await writeFile(filePath, JSON.stringify(output, null, 2));
        console.log(`\n📝 Network log saved to: ${filePath}`);
        console.log(`   Total requests captured: ${this.requests.length}`);
        return filePath;
    }

    reset() {
        this.requests = [];
        this.startTime = Date.now();
    }
}

module.exports = NetworkLogger;
