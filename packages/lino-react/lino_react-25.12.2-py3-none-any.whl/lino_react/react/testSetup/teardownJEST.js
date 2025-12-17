const fs = require('fs').promises;
const os = require('os');
const path = require('path');

const DIR = path.join(os.tmpdir(), 'jest_puppeteer_global_setup');

module.exports = async () => {
    const isRTL = process.env.BABEL === '1';
    const isRTLLogging = process.env.RTL_LOG_NETWORK === '1';
    
    if (isRTL && !isRTLLogging) {
        // RTL tests without logging - nothing to clean up
        return;
    }
    
    if (isRTL && isRTLLogging) {
        // RTL tests with logging - kill RTL server
        if (globalThis.__RTL_SERVER_PROCESS__) {
            console.log('🛑 Stopping RTL Django server...');
            globalThis.__RTL_SERVER_PROCESS__.kill('SIGTERM');
        }
        return;
    }
    
    // Puppeteer tests
    if (globalThis.__BROWSER_GLOBAL__) {
        await globalThis.__BROWSER_GLOBAL__.close();
    }

    await fs.rm(DIR, {recursive: true, force: true});

    if (globalThis.__SERVER_PROCESS__) {
        globalThis.__SERVER_PROCESS__.kill('SIGTERM');
    }
}

