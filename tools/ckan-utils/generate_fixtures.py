#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests", "python-dotenv"]
# ///
"""Generate MSP test fixtures from schema"""
import json, random, requests, os, uuid
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv()
api_key = os.getenv("CKAN_API_KEY")
ckan_url = os.getenv("CKAN_URL", "http://localhost:5000")

# Load schema
schema_path = Path(__file__).parent.parent.parent / 'ckanext/ckanext-schemas/ckanext/schemas/msp_data.json'
schema = json.loads(schema_path.read_text())

# Get cluster fields
clusters = {}
for field in schema['dataset_fields']:
    if 'cluster' in field and field.get('choices'):
        cluster = field['cluster']
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append({
            'name': field['field_name'],
            'choices': [c['value'] for c in field['choices']],
            'multi': field.get('preset') == 'multiple_checkbox'
        })

# Get org
org_resp = requests.get(f"{ckan_url}/api/3/action/organization_show?id=test-msp-org")
if org_resp.json().get('success'):
    org_id = org_resp.json()['result']['id']
else:
    # Create org
    org_data = {'name': 'test-msp-org', 'title': 'Test MSP Org'}
    org_resp = requests.post(f"{ckan_url}/api/3/action/organization_create", 
                           headers={'X-CKAN-API-Key': api_key}, json=org_data)
    org_id = org_resp.json()['result']['id']

# Generate datasets
created = 0
for cluster, fields in clusters.items():
    for i in range(2):  # 2 datasets per cluster
        name = f"test-{cluster}-{str(uuid.uuid4())[:8]}"
        data = {
            'name': name,
            'title': f"Test {cluster.title()} Dataset",
            'type': 'msp-data',
            'notes': f"Generated test dataset for {cluster} cluster",
            'language': 'eng',
            'owner_org': org_id
        }
        
        # Add cluster fields
        field = random.choice(fields)
        if field['multi']:
            data[field['name']] = random.sample(field['choices'], min(2, len(field['choices'])))
        else:
            data[field['name']] = random.choice(field['choices'])
        
        # Create dataset
        resp = requests.post(f"{ckan_url}/api/3/action/package_create",
                           headers={'X-CKAN-API-Key': api_key}, json=data)
        if resp.json().get('success'):
            print(f"✓ {data['name']}")
            created += 1
        else:
            print(f"✗ {data['name']}: {resp.json().get('error', {})}")

print(f"Created {created} datasets")