#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests", "python-dotenv"]
# ///
"""Update all datasets to recompute clusters"""
import requests, os
from dotenv import load_dotenv

# Load env
load_dotenv()
api_key = os.getenv("CKAN_API_KEY")
ckan_url = os.getenv("CKAN_URL", "http://localhost:5000")
headers = {'X-CKAN-API-Key': api_key}

# Get all datasets
start, updated = 0, 0
while True:
    resp = requests.post(f"{ckan_url}/api/3/action/package_search", 
                        headers=headers, 
                        json={'fq': 'type:msp-data', 'start': start, 'rows': 100})
    
    result = resp.json()['result']
    datasets = result['results']
    
    for ds in datasets:
        # Trigger update (recomputes clusters via plugin)
        patch_resp = requests.post(f"{ckan_url}/api/3/action/package_patch",
                                 headers=headers, 
                                 json={'id': ds['id']})
        if patch_resp.json().get('success'):
            print(f"✓ {ds['name']}")
            updated += 1
        else:
            print(f"✗ {ds['name']}")
    
    if len(datasets) < 100:
        break
    start += 100

print(f"Updated {updated} datasets")