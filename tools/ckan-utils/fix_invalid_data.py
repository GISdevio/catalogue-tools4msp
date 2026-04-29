#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests", "python-dotenv"]
# ///
"""Fix datasets with invalid JSON string fields"""
import requests, os, json
from dotenv import load_dotenv

load_dotenv()
headers = {'X-CKAN-API-Key': os.getenv("CKAN_API_KEY")}
ckan_url = os.getenv("CKAN_URL", "http://localhost:5000")

def fix_dataset(dataset_id):
    # Get dataset
    show_resp = requests.post(f"{ckan_url}/api/3/action/package_show",
                            headers=headers, json={'id': dataset_id})
    
    if not show_resp.json().get('success'):
        print(f"✗ Failed to fetch {dataset_id}")
        return False
    
    pkg = show_resp.json()['result']
    print(f"Fixing: {pkg['name']}")
    
    # Fix JSON string fields
    fields_to_fix = ['category', 'web_services', 'domain_area']
    changes_made = False
    
    for field in fields_to_fix:
        if field in pkg and isinstance(pkg[field], str):
            value = pkg[field]
            if value.startswith('[') or value.startswith('{'):
                try:
                    # Parse JSON string and convert to proper format
                    parsed = json.loads(value)
                    pkg[field] = parsed
                    print(f"  Fixed {field}: {value} -> {parsed}")
                    changes_made = True
                except json.JSONDecodeError:
                    print(f"  Could not parse {field}: {value}")
    
    if not changes_made:
        print("  No changes needed")
        return True
    
    # Update the dataset using package_show->package_update approach
    # Remove revision info to avoid conflicts
    for field in ['revision_id', 'revision_timestamp']:
        if field in pkg:
            del pkg[field]
    
    # Use package_update with ckanapi-style call
    update_resp = requests.post(f"{ckan_url}/api/3/action/package_update",
                              headers=headers,
                              json=pkg)
    
    if update_resp.json().get('success'):
        print(f"✓ Successfully fixed {pkg['name']}")
        return True
    else:
        print(f"✗ Failed to update {pkg['name']}")
        print(f"  Error: {update_resp.text}")
        return False

# Test on the specific problematic dataset
dataset_id = 'http-www-geoportal-mrt-gov-me-layers-geonode-vazduh-stalne-stanice-pnt'
fix_dataset(dataset_id)