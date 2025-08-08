from ckanext.scheming.plugins import _load_schemas as load_schemas
from ckan.common import config

from collections import defaultdict

SCHEMA = load_schemas(
    config.get('scheming.dataset_schemas').split(),
    "dataset_type"
)["msp-data"]

CLUSTERS = defaultdict(list)
for field in SCHEMA["dataset_fields"]:
    if "cluster" in field:
        cluster = field["cluster"]
        CLUSTERS[cluster].append(field)

def relevant_clusters(pkg_dict):
    clusters = []
    for cluster, fields in CLUSTERS.items():
        # Skip "relevance" cluster as it's not a real cluster
        if cluster == "relevance":
            continue
            
        for field in fields:
            data = pkg_dict.get(field["field_name"])
            if not data:
                continue
            if field.get("preset") == "multiple_checkbox":
                relevant = len(data) > 0
            elif field.get("preset") == "radio":
                relevant = data == "yes"
            else:
                relevant = data
            if relevant:
                clusters.append(cluster)
                break
    return clusters