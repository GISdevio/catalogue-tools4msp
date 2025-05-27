import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.schemas.views import scheming
import ckanext.schemas.helpers as helpers
import ckanext.schemas.logic.action.get
from ckanext.scheming.plugins import _load_schemas as load_schemas

from ckan.common import config

from collections import defaultdict
import json
import requests
import shapely

CKAN_SOLR_URL = config.get('ckan.solr_url', 'http://solr:8983/solr/ckan')
CKAN_SORL_SCHEMA = CKAN_SOLR_URL + '/schema'

SCHEMA = load_schemas(
    config.get('scheming.dataset_schemas').split(),
    "dataset_type"
)["msp-data"]

CLUSTERS = defaultdict(list)
for field in SCHEMA["dataset_fields"]:
    if "cluster" in field:
        cluster = field["cluster"]
        CLUSTERS[cluster].append(field)

class SchemasPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)

    # IBlueprint
    def get_blueprint(self):
        return [scheming]

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'schemas')

        for field_name in "minx miny maxx maxy".split():
            response = requests.post(CKAN_SORL_SCHEMA, json={
                "add-field": {
                    "name": field_name,
                    "type": "float",
                    "indexed": True,
                    "stored": True,
                }
            })
            response.raise_for_status()

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        for facet in ('organization', 'groups', 'tags', 'res_format', 'license_id'):
            if facet in facets_dict:
                del facets_dict[facet]
        facets_dict['vocab_category'] = toolkit._('Category')
        facets_dict['sub_category'] = toolkit._('Sub Category')
        facets_dict['owner'] = toolkit._('Owner')
        facets_dict['vocab_web_services'] = toolkit._('Web services')
        facets_dict['vocab_domain_area'] = toolkit._('Domain area')
        facets_dict['vocab_clusters'] = toolkit._('Clusters')
        facets_dict['metadata_completeness'] = toolkit._('Metadata completeness')
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        return self.dataset_facets(facets_dict, package_type)

    def organization_facets(self, facets_dict, organization_type, package_type):
        return self.dataset_facets(facets_dict, package_type)

    # IPackageController

    def before_index(self, pkg_dict):
        for field in ('derives_from', 'child_of'):
            data = pkg_dict.get(field+'_string')
            if data:
                data = data.split(',')
            else:
                data = []
            pkg_dict[field] = data
        for field in ('category', 'web_services', 'domain_area'):
            data = pkg_dict.get(field)
            if data:
                try:
                    data = json.loads(data)
                except ValueError:
                    data = data.split(',')
            else:
                data = []
            pkg_dict["vocab_"+field] = data

        geojson = pkg_dict.get("spatial_geojson")
        if not geojson:
            geometry = None
        else:
            try:
                geometry = json.loads(geojson)
            except json.decoder.JSONDecodeError:
                geometry = None
        if geometry:
            shape = shapely.geometry.shape(geometry)
            minx, miny, maxx, maxy = shape.bounds
            pkg_dict["minx"] = minx
            pkg_dict["maxx"] = maxx
            pkg_dict["miny"] = miny
            pkg_dict["maxy"] = maxy
            pkg_dict["spatial_geom"] = shape.wkt

        pkg_dict["vocab_clusters"] = []
        for cluster, fields in CLUSTERS.items():
            for field in fields:
                data = pkg_dict.get(field["field_name"])
                if field.get("preset") == "multiple_checkbox":
                    relevant = len(json.loads(data)) > 0
                elif field.get("preset") == "radio":
                    relevant = data == "yes"
                else:
                    relevant = data
                if relevant:
                    pkg_dict["vocab_clusters"].append(cluster)
                    break

        return pkg_dict

    # ITemplateHelpers

    def get_helpers(self):
        return { name:getattr(helpers, name) for name in dir(helpers) }

    # IActions

    def get_actions(self):
        return {
           'ckan_package_show':
               ckanext.schemas.logic.action.get.ckan_package_show,
           'package_show':
               ckanext.schemas.logic.action.get.package_show,
        }
