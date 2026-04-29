import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan.common import config

from collections import defaultdict
import json
import requests
import shapely

from ckanext.schemas.views import scheming
import ckanext.schemas.helpers as helpers
import ckanext.schemas.utils as utils
from ckanext.scheming.plugins import _load_schemas as load_schemas

# Import action modules
import ckanext.schemas.logic.action.get
import ckanext.schemas.logic.action.create
import ckanext.schemas.logic.action.update

def _get_solr_schema_url():
    solr_url = config.get('ckan.solr_url', 'http://solr:8983/solr/ckan')
    if solr_url and '://' in solr_url:
        return solr_url + '/schema'
    return None

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

        # Try to configure Solr schema if available
        solr_schema_url = _get_solr_schema_url()
        if solr_schema_url:
            try:
                for field_name in "minx miny maxx maxy".split():
                    response = requests.post(solr_schema_url, json={
                        "add-field": {
                            "name": field_name,
                            "type": "float",
                            "indexed": True,
                            "stored": True,
                        }
                    }, timeout=5)
                    # Don't fail if solr is not available yet
            except (requests.exceptions.RequestException, Exception) as e:
                # Log error but don't fail startup
                print(f"Warning: Could not configure Solr schema: {e}")
        else:
            print("Warning: Solr URL not configured or invalid")

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

        pkg_dict["vocab_clusters"] = utils.relevant_clusters(pkg_dict)

        return pkg_dict

    # ITemplateHelpers

    def get_helpers(self):
        return { name:getattr(helpers, name) for name in dir(helpers) }

    # IActions

    def get_actions(self):
        return {
            'ckan_package_show': ckanext.schemas.logic.action.get.ckan_package_show,
            'package_show': ckanext.schemas.logic.action.get.package_show,
            'ckan_package_create': ckanext.schemas.logic.action.create.ckan_package_create,
            'ckan_package_update': ckanext.schemas.logic.action.update.ckan_package_update,
            'package_create': ckanext.schemas.logic.action.create.package_create,
            'package_update': ckanext.schemas.logic.action.update.package_update,
        }
