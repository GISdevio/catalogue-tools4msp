#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests", "python-dotenv"]
# ///
"""Find datasets with invalid tag data"""
import requests, os, re
from dotenv import load_dotenv

load_dotenv()
headers = {'X-CKAN-API-Key': os.getenv("CKAN_API_KEY")}
ckan_url = os.getenv("CKAN_URL", "http://localhost:5000")

print("Finding datasets with invalid data...")
invalid_datasets = []
start = 0

while True:
    resp = requests.post(f"{ckan_url}/api/3/action/package_search", 
                        headers=headers, 
                        json={'fq': 'type:msp-data', 'start': start, 'rows': 100})
    
    datasets = resp.json()['result']['results']
    if not datasets:
        break
    
    for ds in datasets:
        # Check for invalid tag formats
        invalid_reasons = []
        
        # Get full dataset to check all fields
        show_resp = requests.post(f"{ckan_url}/api/3/action/package_show",
                                headers=headers, json={'id': ds['id']})
        if not show_resp.json().get('success'):
            continue
            
        full_data = show_resp.json()['result']
        
        # Check tags field
        if 'tags' in full_data:
            for tag in full_data['tags']:
                if 'name' in tag:
                    tag_name = tag['name']
                    # Check for brackets, quotes, or non-alphanumeric chars (except -_.)
                    if re.search(r'[^\w\-_.]', tag_name):
                        invalid_reasons.append(f"Invalid tag: {tag_name}")
        
        # Check category field (looking for JSON strings)
        for field in ['category', 'web_services', 'domain_area']:
            if field in full_data:
                value = full_data[field]
                if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                    invalid_reasons.append(f"JSON string in {field}: {value[:50]}...")
        
        if invalid_reasons:
            invalid_datasets.append({
                'id': ds['id'],
                'name': ds['name'],
                'title': ds.get('title', ''),
                'reasons': invalid_reasons
            })
            print(f"INVALID: {ds['name']}")
            for reason in invalid_reasons:
                print(f"  - {reason}")
    
    start += len(datasets)

print(f"\nFound {len(invalid_datasets)} datasets with invalid data:")
for ds in invalid_datasets:
    print(f"- {ds['name']}: {', '.join(ds['reasons'])}")