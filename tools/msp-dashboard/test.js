#!/usr/bin/env node
/**
 * Automated end-to-end test for MSP Dashboard
 * 
 * This test validates the dashboard functionality by:
 * 1. Starting a local HTTP server
 * 2. Loading the dashboard in a headless browser
 * 3. Validating data loading, processing, and visualization
 * 4. Outputting structured results for Claude Code validation
 */

const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const { promisify } = require('util');
const sleep = promisify(setTimeout);

// For Node.js < 18, we need to use a fetch polyfill
let fetch;
try {
    fetch = globalThis.fetch;
} catch (e) {
    // Fallback for older Node.js versions
    fetch = async (url) => {
        const http = require('http');
        return new Promise((resolve, reject) => {
            const req = http.get(url, (res) => {
                resolve({ ok: res.statusCode === 200 });
            });
            req.on('error', reject);
            req.setTimeout(5000, () => req.destroy());
        });
    };
}

class DashboardTest {
    constructor() {
        this.server = null;
        this.browser = null;
        this.page = null;
        this.port = 8080; // Use Caddy default port
        this.results = {
            serverStart: false,
            pageLoad: false,
            apiConnection: false,
            dataLoading: false,
            clusterProcessing: false,
            chartRendering: false,
            totalDatasets: 0,
            totalClusters: 0,
            errors: []
        };
    }

    async run() {
        console.log('🧪 MSP Dashboard End-to-End Test');
        console.log('================================');
        
        try {
            await this.startServer();
            await this.setupBrowser();
            await this.loadDashboard();
            await this.validateDashboard();
            
            this.printResults();
            return this.getExitCode();
            
        } catch (error) {
            console.error('❌ Test failed with error:', error.message);
            this.results.errors.push(error.message);
            return 1;
        } finally {
            await this.cleanup();
        }
    }

    async startServer() {
        console.log('🚀 Checking for existing server...');
        
        // First, check if a server is already running on this port
        const isServerRunning = await this.checkServerRunning();
        if (isServerRunning) {
            console.log(`✓ Server already running on port ${this.port}`);
            this.results.serverStart = true;
            return;
        }
        
        console.log('🚀 Starting Caddy server...');
        
        return new Promise((resolve, reject) => {
            this.server = spawn('caddy', ['run', '--config', 'Caddyfile'], {
                cwd: __dirname,
                stdio: 'pipe'
            });

            let serverStarted = false;

            this.server.stdout.on('data', (data) => {
                const output = data.toString();
                console.log('Caddy output:', output.trim());
                if ((output.includes('serving initial configuration') || output.includes('admin serving initial configuration')) && !serverStarted) {
                    serverStarted = true;
                    console.log('✓ Caddy server started on port', this.port);
                    this.results.serverStart = true;
                    setTimeout(resolve, 3000); // Give Caddy time to fully start
                }
            });

            this.server.stderr.on('data', (data) => {
                const error = data.toString();
                if (error.includes('address already in use') || error.includes('bind: address already in use')) {
                    this.port = this.port + 1;
                    this.server.kill();
                    this.startServer().then(resolve).catch(reject);
                } else {
                    // Caddy logs go to stderr, some are not errors
                    if (!error.includes('GET ') && !error.includes('POST ')) {
                        console.error('Caddy error:', error.trim());
                    }
                }
            });

            this.server.on('error', (error) => {
                reject(new Error(`Failed to start server: ${error.message}`));
            });

            // Fallback: try to detect server by attempting connection
            setTimeout(async () => {
                if (!serverStarted) {
                    try {
                        const response = await fetch(`http://localhost:${this.port}`);
                        if (response.ok) {
                            console.log('✓ Server detected via HTTP check on port', this.port);
                            this.results.serverStart = true;
                            serverStarted = true;
                            resolve();
                        }
                    } catch (e) {
                        // Still starting
                    }
                }
            }, 3000);

            // Timeout after 15 seconds
            setTimeout(() => {
                if (!serverStarted) {
                    reject(new Error('Server start timeout'));
                }
            }, 15000);
        });
    }

    async checkServerRunning() {
        try {
            const response = await fetch(`http://localhost:${this.port}`);
            return response.ok;
        } catch (e) {
            return false;
        }
    }

    async setupBrowser() {
        console.log('🌐 Setting up headless browser...');
        
        this.browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        this.page = await this.browser.newPage();
        
        // Enable console logging from the page
        this.page.on('console', msg => {
            console.log(`Browser console [${msg.type()}]:`, msg.text());
            if (msg.type() === 'error') {
                this.results.errors.push(`Browser console error: ${msg.text()}`);
            }
        });

        // Track network requests
        this.page.on('requestfailed', request => {
            console.log('Network request failed:', request.url(), request.failure()?.errorText);
            this.results.errors.push(`Network request failed: ${request.url()} - ${request.failure()?.errorText}`);
        });

        console.log('✓ Browser setup complete');
    }

    async loadDashboard() {
        console.log('📄 Loading dashboard page...');
        
        const url = `http://localhost:${this.port}`;
        
        try {
            await this.page.goto(url, { 
                waitUntil: 'networkidle0',
                timeout: 30000 
            });
            
            console.log('✓ Dashboard page loaded');
            this.results.pageLoad = true;
            
        } catch (error) {
            throw new Error(`Failed to load dashboard: ${error.message}`);
        }
    }

    async validateDashboard() {
        console.log('🔍 Validating dashboard functionality...');
        
        // Wait for loading to complete (max 30 seconds)
        await this.waitForLoadingComplete();
        
        // Check if dashboard is visible (not loading or error state)
        const dashboardVisible = await this.page.$('#dashboard[style*="display: block"], #dashboard:not([style*="display: none"])');
        if (!dashboardVisible) {
            const errorVisible = await this.page.$('#error[style*="display: block"], #error:not([style*="display: none"])');
            if (errorVisible) {
                const errorText = await this.page.$eval('#error', el => el.textContent);
                throw new Error(`Dashboard shows error state: ${errorText}`);
            } else {
                throw new Error('Dashboard not visible and not in error state');
            }
        }

        await this.validateApiConnection();
        await this.validateDataLoading();
        await this.validateClusterProcessing();
        await this.validateChartRendering();
    }

    async waitForLoadingComplete() {
        console.log('⏳ Waiting for data loading to complete...');
        
        try {
            // Wait for loading element to disappear or dashboard to appear
            await this.page.waitForFunction(() => {
                const loading = document.getElementById('loading');
                const dashboard = document.getElementById('dashboard');
                const error = document.getElementById('error');
                
                const loadingHidden = !loading || loading.style.display === 'none';
                const dashboardVisible = dashboard && dashboard.style.display !== 'none';
                const errorVisible = error && error.style.display !== 'none';
                
                return loadingHidden && (dashboardVisible || errorVisible);
            }, { timeout: 30000 });
            
        } catch (error) {
            throw new Error('Timeout waiting for dashboard to load data');
        }
    }

    async validateApiConnection() {
        // Check for successful API calls (no network errors captured)
        const hasNetworkErrors = this.results.errors.some(error => 
            error.includes('Network request failed') || error.includes('CKAN API')
        );
        
        this.results.apiConnection = !hasNetworkErrors;
        console.log(this.results.apiConnection ? '✓ API connection successful' : '❌ API connection failed');
    }

    async validateDataLoading() {
        try {
            // Get total datasets count
            const totalDatasets = await this.page.$eval('#total-datasets', el => parseInt(el.textContent));
            this.results.totalDatasets = totalDatasets;
            this.results.dataLoading = totalDatasets > 0;
            
            console.log(`✓ Data loading: ${totalDatasets} datasets loaded`);
            
        } catch (error) {
            this.results.dataLoading = false;
            console.log('❌ Data loading validation failed');
            this.results.errors.push('Could not read total datasets count');
        }
    }

    async validateClusterProcessing() {
        try {
            // Get total clusters count
            const totalClusters = await this.page.$eval('#total-clusters', el => parseInt(el.textContent));
            this.results.totalClusters = totalClusters;
            this.results.clusterProcessing = totalClusters > 0;
            
            console.log(`✓ Cluster processing: ${totalClusters} clusters identified`);
            
        } catch (error) {
            this.results.clusterProcessing = false;
            console.log('❌ Cluster processing validation failed');
            this.results.errors.push('Could not read total clusters count');
        }
    }

    async validateChartRendering() {
        try {
            // Give Vega-Lite more time to render
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Check for either SVG or canvas elements (Vega-Lite can use both)
            const svgElements = await this.page.$$('#cluster-chart svg');
            const canvasElements = await this.page.$$('#cluster-chart canvas');
            const hasVisualization = svgElements.length > 0 || canvasElements.length > 0;
            
            // Also check if the chart container has content
            const chartContainer = await this.page.$('#cluster-chart');
            const hasContent = chartContainer && await this.page.evaluate(el => el.innerHTML.trim() !== '', chartContainer);
            
            this.results.chartRendering = hasVisualization || hasContent;
            
            console.log(this.results.chartRendering ? 
                '✓ Chart rendering: Visualization present' : 
                '❌ Chart rendering failed');
            
        } catch (error) {
            this.results.chartRendering = false;
            console.log('❌ Chart rendering validation failed');
            this.results.errors.push('Chart visualization elements not found');
        }
    }


    printResults() {
        console.log('\n📊 Test Results Summary');
        console.log('=======================');
        
        const checks = [
            ['Server Start', this.results.serverStart],
            ['Page Load', this.results.pageLoad],
            ['API Connection', this.results.apiConnection],
            ['Data Loading', this.results.dataLoading],
            ['Cluster Processing', this.results.clusterProcessing],
            ['Chart Rendering', this.results.chartRendering]
        ];

        checks.forEach(([name, passed]) => {
            console.log(`${passed ? '✓' : '❌'} ${name}: ${passed ? 'PASS' : 'FAIL'}`);
        });

        if (this.results.dataLoading) {
            console.log(`📈 Datasets: ${this.results.totalDatasets}`);
            console.log(`🏷️  Clusters: ${this.results.totalClusters}`);
        }

        if (this.results.errors.length > 0) {
            console.log('\n⚠️  Errors encountered:');
            this.results.errors.forEach(error => console.log(`   - ${error}`));
        }

        const allPassed = checks.every(([_, passed]) => passed);
        console.log(`\n🎯 Overall Status: ${allPassed ? 'PASS' : 'FAIL'}`);
    }

    getExitCode() {
        const criticalChecks = [
            this.results.serverStart,
            this.results.pageLoad,
            this.results.apiConnection,
            this.results.dataLoading,
            this.results.clusterProcessing
        ];
        
        return criticalChecks.every(check => check) ? 0 : 1;
    }

    async cleanup() {
        console.log('\n🧹 Cleaning up...');
        
        if (this.browser) {
            await this.browser.close();
        }
        
        if (this.server && this.server.pid) {
            console.log('Stopping server process...');
            try {
                process.kill(this.server.pid, 'SIGTERM');
                // Give it a moment to terminate gracefully
                await sleep(1000);
                if (this.server.killed === false) {
                    process.kill(this.server.pid, 'SIGKILL');
                }
            } catch (e) {
                // Process might already be dead
            }
        }
    }
}

// Run the test
if (require.main === module) {
    const test = new DashboardTest();
    test.run().then(exitCode => {
        process.exit(exitCode);
    }).catch(error => {
        console.error('Test runner error:', error);
        process.exit(1);
    });
}

module.exports = DashboardTest;