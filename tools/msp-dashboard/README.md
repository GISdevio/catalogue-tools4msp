# MSP Dashboard

Simple web dashboard for visualizing MSP datasets from https://catalogue.tools4msp.eu.

## Quick Start

```bash
caddy run --config Caddyfile
```

Open http://localhost:8080

## What it does

- Fetches MSP data via CKAN API
- Groups datasets by clusters  
- Shows bar chart with Vega-Lite
- Displays summary statistics

## Files

- `index.html` - Dashboard page
- `assets/main.js` - API calls and data processing
- `assets/styles.css` - Basic styling
- `Caddyfile` - CORS proxy configuration
- `test.js` - End-to-end test

## Testing

```bash
node test.js
```

Requires `puppeteer` for automated browser testing.