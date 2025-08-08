// CKAN API configuration
//const CKAN_API_BASE = '/api/3/action/';
const CKAN_API_BASE = 'https://catalogue.tools4msp.eu/api/3/action/';
const DATASETS_PER_PAGE = 1000;

// Global data storage
let clusterStats = {};

// DOM elements
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const dashboardEl = document.getElementById('dashboard');
const totalDatasetsEl = document.getElementById('total-datasets');
const totalClustersEl = document.getElementById('total-clusters');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadAllDatasets();
});

// Fetch all datasets with pagination
async function loadAllDatasets() {
    try {
        showLoading();
        
        let start = 0;
        let totalCount = 0;
        let processedCount = 0;
        
        do {
            const params = new URLSearchParams({
                fq: 'type:msp-data',
                rows: DATASETS_PER_PAGE,
                start: start
            });
            
            const url = `${CKAN_API_BASE}package_search?${params}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error('CKAN API returned error: ' + (data.error?.message || 'Unknown error'));
            }
            
            const results = data.result.results;
            totalCount = data.result.count;
            
            // Process this batch directly
            processDataBatch(results);
            processedCount += results.length;
            
            start += DATASETS_PER_PAGE;
            
            // Update loading message
            loadingEl.textContent = `Loading datasets... (${processedCount}/${totalCount})`;
            
        } while (start < totalCount);
        
        finalizeClusters(totalCount);
        renderDashboard();
        hideLoading();
        
    } catch (error) {
        console.error('Error loading datasets:', error);
        showError();
    }
}

// Process a batch of datasets
function processDataBatch(datasets) {    
    // Count datasets per cluster using clusters field from API
    datasets.forEach(dataset => {
        const clusters = dataset.clusters || [];
        clusters.forEach(cluster => {
            clusterStats[cluster] = (clusterStats[cluster] || 0) + 1;
        });
    });
}

// Finalize cluster processing and update UI
function finalizeClusters(totalCount) {
    totalDatasetsEl.textContent = totalCount;
    totalClustersEl.textContent = Object.keys(clusterStats).length;
}

// Render the complete dashboard
function renderDashboard() {
    renderClusterChart();
}

// Render simple cluster chart using pre-computed clusterStats
function renderClusterChart() {
    // Convert clusterStats to chart data
    const chartData = Object.entries(clusterStats).map(([cluster, count]) => ({
        cluster: cluster,
        count: count
    }));
    
    const spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "values": chartData
        },
        "mark": {
            "type": "bar",
            "color": "#2563eb"
        },
        "encoding": {
            "x": {
                "field": "cluster",
                "type": "nominal",
                "axis": {
                    "title": "MSP Cluster",
                    "labelAngle": -45
                }
            },
            "y": {
                "field": "count",
                "type": "quantitative",
                "axis": {
                    "title": "Number of Datasets"
                }
            },
            "tooltip": [
                {"field": "cluster", "type": "nominal", "title": "Cluster"},
                {"field": "count", "type": "quantitative", "title": "Datasets"}
            ]
        },
        "width": 600,
        "height": 400
    };
    
    vegaEmbed('#cluster-chart', spec, {
        theme: 'default',
        actions: false
    }).catch(console.error);
}


// Utility functions
function showLoading() {
    loadingEl.style.display = 'block';
    errorEl.style.display = 'none';
    dashboardEl.style.display = 'none';
}

function hideLoading() {
    loadingEl.style.display = 'none';
    dashboardEl.style.display = 'block';
}

function showError() {
    loadingEl.style.display = 'none';
    errorEl.style.display = 'block';
    dashboardEl.style.display = 'none';
}

