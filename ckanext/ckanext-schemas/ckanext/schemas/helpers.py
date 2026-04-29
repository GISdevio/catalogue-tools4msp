from ckan.common import config

import json
import os.path

file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'presets')

with open(os.path.join(file_dir, 'categories.json')) as categories_file:
    categories = json.load(categories_file)

def scheming_categories_choices(field):
    return categories

# Load domainareas dynamically
def _load_domainareas():
    domainareas_path = config.get('ckan.domainareas_path')
    if domainareas_path and os.path.exists(domainareas_path):
        with open(domainareas_path) as f:
            return json.load(f)
    return []

def scheming_domainareas_choices(field):
    domainareas = _load_domainareas()
    for domainarea in domainareas:
        yield {
            'value': domainarea['label'].lower().replace(' ', '_').replace('&', '_'),
            'label': domainarea['label'],
        }

