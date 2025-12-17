const {mkdir, writeFile} = require('fs').promises;
const {spawn} = require('child_process');
const os = require('os');
const path = require('path');
const puppeteer = require('puppeteer');
const { get } = require('http');

const DIR = path.join(os.tmpdir(), 'jest_puppeteer_global_setup');

// Wait for server to be ready
async function waitForServer(url, timeout = 30000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
        try {
            const ready = await new Promise((resolve) => {
                get(url, (res) => {
                    resolve(res.statusCode === 200);
                }).on('error', () => {
                    resolve(false);
                });
            });
            
            if (ready) {
                return true;
            }
        } catch (error) {
            // Server not ready yet
        }
        
        await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    throw new Error(`Server at ${url} failed to start within ${timeout}ms`);
}

module.exports = async (globalConfig, projectConfig) => {
    const isRTL = process.env.BABEL === '1';
    const isRTLLogging = process.env.RTL_LOG_NETWORK === '1';
    
    if (isRTL && !isRTLLogging) {
        // RTL tests without logging - no server needed, MSW will use cached responses
        console.log('🎭 RTL tests will use cached network responses');
        return;
    }
    
    if (isRTL && isRTLLogging) {
        // RTL tests with live logging - start Django server on port 3001
        console.log('🚀 Starting Django server for RTL network logging...');
        
        const mpy = path.resolve(__dirname).split(path.sep).slice(0, -3)
            .join(path.sep) + `/puppeteers/${process.env.BASE_SITE}/manage.py`;
        
        console.log(`📁 Starting server from: ${mpy}`);
        
        // Activate virtual environment and run server
        const venvActivate = '/home/blurry/lino/env/bin/activate';
        const command = `source ${venvActivate} && python ${mpy} runserver 127.0.0.1:3001`;
        
        globalThis.__RTL_SERVER_PROCESS__ = spawn(
            'bash',
            ['-c', command],
            {
                stdio: ['ignore', 'pipe', 'pipe'],
                detached: false
            }
        );
        
        // Capture server output for debugging
        let serverOutput = '';
        globalThis.__RTL_SERVER_PROCESS__.stdout.on('data', (data) => {
            serverOutput += data.toString();
        });
        globalThis.__RTL_SERVER_PROCESS__.stderr.on('data', (data) => {
            serverOutput += data.toString();
        });
        
        globalThis.__RTL_SERVER_PROCESS__.on('error', (error) => {
            console.error('❌ Failed to start Django server:', error);
            throw error;
        });
        
        // Wait for RTL server to be ready
        console.log('⏳ Waiting for RTL Django server to start on port 3001...');
        try {
            await waitForServer('http://127.0.0.1:3001');
            console.log('✅ RTL Django server is ready on port 3001');
        } catch (error) {
            console.error('❌ Server failed to start. Output:');
            console.error(serverOutput);
            throw error;
        }
        
        return;
    }
    
    // Puppeteer tests (BABEL !== '1')
    let browser;
    if (process.getuid() == 0) {
        browser = await puppeteer.launch({
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
            protocolTimeout: 120000,
        });
    } else {
        browser = await puppeteer.launch({headless: false});
        // browser = await puppeteer.launch();
    }

    globalThis.__BROWSER_GLOBAL__ = browser;

    await mkdir(DIR, {recursive: true});
    await writeFile(path.join(DIR, 'wsEndpoint'), browser.wsEndpoint());

    const mpy = path.resolve(__dirname).split(path.sep).slice(0, -3)
        .join(path.sep) + `/puppeteers/${process.env.BASE_SITE}/manage.py`;
    globalThis.__SERVER_PROCESS__ = spawn(
        "python",
        [mpy, "runserver", "127.0.0.1:3000"],
        {stdio: 'ignore'}
    );
    
    // Wait for Puppeteer server to be ready
    console.log('⏳ Waiting for Puppeteer Django server to start...');
    await waitForServer('http://127.0.0.1:3000');
    console.log('✅ Puppeteer Django server is ready on port 3000');
}

