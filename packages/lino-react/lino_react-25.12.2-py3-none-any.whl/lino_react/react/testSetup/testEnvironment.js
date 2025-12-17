const {readFile} = require('fs').promises;
const os = require('os');
const path = require('path');
const puppeteer = require('puppeteer');
const NodeEnvironment = require('jest-environment-node').TestEnvironment;
const NetworkLogger = require('../../../network-testing/networkLogger');

const DIR = path.join(os.tmpdir(), 'jest_puppeteer_global_setup');

class PuppeteerEnvironment extends NodeEnvironment {
    constructor(config) {
        super(config);
    }

    async setup() {
        await super.setup();
        if (process.env.BABEL === '1') {
            return;
        }

        const wsEndpoint = await readFile(path.join(DIR, 'wsEndpoint'), 'utf8');
        if (!wsEndpoint) throw new Error('wsEndpoint not found');

        this.global.__BROWSER_GLOBAL__ = await puppeteer.connect({
            browserWSEndpoint: wsEndpoint
        });

        // Setup network logging if enabled
        if (process.env.LOG_NETWORK === '1') {
            this.global.networkLogger = new NetworkLogger('./network-testing/logs');
            console.log('🌐 Network logging enabled. Logs will be saved to ./network-logs/');

            // Wrap newPage to automatically setup network logging
            const originalNewPage = this.global.__BROWSER_GLOBAL__.newPage.bind(this.global.__BROWSER_GLOBAL__);
            this.global.__BROWSER_GLOBAL__.newPage = async function(...args) {
                const page = await originalNewPage(...args);
                if (this.networkLogger) {
                    await this.networkLogger.setupPage(page);
                    console.log('📡 Network logging setup for new page');
                }
                return page;
            }.bind(this.global);
        }
    }

    async teardown() {
        if (process.env.BABEL === '1') {
            await super.teardown();
            return;
        }
        if (this.global.__BROWSER_GLOBAL__)
            this.global.__BROWSER_GLOBAL__.disconnect();

        await super.teardown();
    }

    getVmContext() {
        return super.getVmContext();
    }
}

module.exports = PuppeteerEnvironment;
