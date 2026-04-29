#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests", "python-dotenv"]
# ///
import requests, os, json
from dotenv import load_dotenv

load_dotenv()
headers = {'X-CKAN-API-Key': os.getenv("CKAN_API_KEY")}
ckan_url = os.getenv("CKAN_URL", "http://localhost:5000")

fixed, failed = 0, 0
start = 0

while True:
    resp = requests.post(f"{ckan_url}/api/3/action/package_search", 
                        headers=headers, 
                        json={'fq': 'type:msp-data', 'start': start, 'rows': 100})
    resp.raise_for_status()
    
    datasets = resp.json()['result']['results']
    if not datasets:
        break
    
    for ds in datasets:
        show_resp = requests.post(f"{ckan_url}/api/3/action/package_show",
                                headers=headers, json={'id': ds['id']})
        show_resp.raise_for_status()
        pkg = show_resp.json()['result']
        
        patch_data = {'id': ds['id']}
        changes_made = False
        
        # Fix JSON string fields
        for field in ['category', 'web_services', 'domain_area']:
            if field in pkg and isinstance(pkg[field], str) and pkg[field].startswith('['):
                try:
                    patch_data[field] = json.loads(pkg[field])
                    changes_made = True
                    print(f"Will fix {ds['name']} {field}")
                except json.JSONDecodeError:
                    pass
        
        # Fix invalid mspkc_resource_type
        fixed_resources = []
        for resource in pkg.get('resources', []):
            if 'mspkc_resource_type' in resource:
                old_type = resource['mspkc_resource_type']
                valid_types = ['WebService', 'GeospatialDataset', 'MapViewer', 'WebPage', 'Document', 'Metadata', 'Other', 'OtherAddInfo']
                if old_type not in valid_types:
                    resource['mspkc_resource_type'] = 'Other'
                    changes_made = True
                    print(f"Will fix {ds['name']} resource type: {old_type} -> Other")
            fixed_resources.append(resource)
        
        if fixed_resources and any('mspkc_resource_type' in r for r in pkg.get('resources', [])):
            patch_data['resources'] = fixed_resources
            changes_made = True
        
        if changes_made:
            patch_resp = requests.post(f"{ckan_url}/api/3/action/package_patch",
                                      headers=headers, json=patch_data)
            if patch_resp.status_code == 200 and patch_resp.json().get('success'):
                print(f"✓ Fixed: {ds['name']}")
                fixed += 1
            else:
                print(f"✗ Failed: {ds['name']}")
                print(patch_resp.text)
                failed += 1
    
    start += len(datasets)

print(f"Fixed: {fixed}, Failed: {failed}")