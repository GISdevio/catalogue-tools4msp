#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests", "python-dotenv"]
# ///
"""Debug cluster computation"""
import requests, os, sys
sys.path.insert(0, '/home/frafra/Code/catalogue-tools4msp/ckanext/ckanext-schemas')

from dotenv import load_dotenv
import ckanext.schemas.utils as utils

# Load env
load_dotenv()
api_key = os.getenv("CKAN_API_KEY")
ckan_url = os.getenv("CKAN_URL")
headers = {'X-CKAN-API-Key': api_key}

# Get a specific dataset
resp = requests.post(f"{ckan_url}/api/3/action/package_show", 
                    headers=headers, 
                    json={'id': 'emodnet-impulsive-anthropogenic-sound'})

pkg = resp.json()['result']
print("Dataset title:", pkg['title'])

# Test cluster computation
clusters = utils.relevant_clusters(pkg)
print("Computed clusters:", clusters)
print("Type:", type(clusters))
print("Is truthy:", bool(clusters))

# Show relevant field values
cluster_fields = ['environment-msfd-classes', 'maritime-activities', 'conservation-types']
for field in cluster_fields:
    value = pkg.get(field, 'NOT_FOUND')
    print(f'{field}: {value}')