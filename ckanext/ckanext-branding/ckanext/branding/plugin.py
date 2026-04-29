import json
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.logic import NotFound

from ckan.common import config


def get_featured_categories():
    '''Return the value of featured categories config setting.

    To enable showing the most popular groups, add this line to the
    [app:main] section of your CKAN config file::

      ckan.branding.featured_categories = ''

    '''
    value = config.get('ckan.branding.featured_categories', '[]')
    if value == '':
        value = '[]'
    try:
        value = json.loads(value)
    except ValueError:
        value = [{'icon': 'fa-triangle-exclamation', 'label': 'Error decoding featured categories' }]
    return value


def get_featured_datasets():
    '''Return the value of the featured datasets config setting.

    To enable showing the most popular groups, add this line to the
    [app:main] section of your CKAN config file::

      ckan.branding.featured_datasets = ''

    '''
    value = config.get('ckan.branding.featured_datasets', '[]')
    if value == '':
        value = '[]'
    try:
        value = json.loads(value)
    except ValueError:
        value = [{'icon': 'fa-triangle-exclamation', 'label': 'Error decoding featured datasets' }]
    return value

def get_branding_featured_groups():
    '''Return the value of the featured groups config setting.

    To enable showing the most popular groups, add this line to the
    [app:main] section of your CKAN config file::

      ckan.branding.featured_groups = ''

    '''
    config_groups = config.get('ckan.branding.featured_groups', "[]")
    try:
        config_groups = json.loads(config_groups)
    except ValueError:
        config_groups = list()

    groups_data = []

    for group_name in config_groups:
        try:
            group = toolkit.get_action('group_show')({}, {'id': group_name, 'include_datasets': True})
            if group:
                groups_data.append(group)
        except NotFound:
            pass

    return groups_data


def branding_simple_list_config(value, context):
    if value == "":
        return "[]"
    try:
        val = json.loads(value)
    except ValueError:
        raise toolkit.Invalid('Should be a valid JSON string')
    
    if type(val) is not list:
        raise toolkit.Invalid('Root should be a json array - example: []')

    for idx, element in enumerate(val):
        if not isinstance(element, str):
            raise toolkit.Invalid(f'Element {idx} should be a string')

    return value

def branding_list_config(value, context):
    if value == "":
        return "[]"
    try:
        val = json.loads(value)
    except ValueError:
        raise toolkit.Invalid('Should be a valid JSON string')
    
    if type(val) is not list:
        raise toolkit.Invalid('Root should be a json array - example: [{ ... }]')
    
    for idx, element in enumerate(val):
        if not type(element) is dict:
            raise toolkit.Invalid(f'Element {idx} should be a json object - example: {{ "key": "value" }}')
        if "label" not in element:
            raise toolkit.Invalid(f'Element {idx} should contain a "label" - example: {{ "label": "value" }}')
        if "icon" not in element:       
            raise toolkit.Invalid(f'Element {idx} should contain an "icon" - example: {{ "icon": "fa-fish" }}')
        if "url" not in element:       
            raise toolkit.Invalid(f'Element {idx} should contain an "url" - example: {{ "url": "dataset_identifier_or_category_identifier" }}')

    return value


class BrandingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigDeclaration)
    plugins.implements(plugins.ITemplateHelpers)


    # IConfigDeclaration
    
    def declare_config_options(self, declaration, key):
        declaration.declare(key.ckan.branding.featured_categories, "[]").set_description(
            "JSON list of featured categories for homepage"
        )
        declaration.declare(key.ckan.branding.featured_datasets, "[]").set_description(
            "JSON list of featured datasets for homepage"
        )
        declaration.declare(key.ckan.branding.featured_groups, "[]").set_description(
            "JSON list of featured groups for homepage"
        )

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'branding')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        unicode_safe = toolkit.get_validator('unicode_safe')
        schema.update({
            'ckan.branding.featured_categories': [ignore_missing, unicode_safe, branding_list_config],
            'ckan.branding.featured_datasets': [ignore_missing, unicode_safe, branding_list_config],
            'ckan.branding.featured_groups': [ignore_missing, unicode_safe, branding_simple_list_config],
        })
        return schema

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'branding_featured_categories': get_featured_categories,
            'branding_featured_datasets': get_featured_datasets,
            'branding_featured_groups': get_branding_featured_groups,
        }
