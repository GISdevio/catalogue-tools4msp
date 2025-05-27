#!/bin/bash
set -e

/ckan-entrypoint.sh

conf="/etc/ckan/production.ini"
function conf_set() { crudini --set "$conf" app:main "$@"; }
function conf_get() { crudini --get "$conf" app:main "$@"; }
function conf_set_list() {
    param="$1"
    shift
    for var in "$@"; do
        crudini --set --list --list-sep=' ' "$conf" app:main "$param" "$var"
    done
}

#ckan
crudini --set "$conf" DEFAULT debug "false"
conf_set ckan.site_title "Tools4MSP"
conf_set ckan.site_description "This is the portal of the catalogue-tools4msp project."
conf_set ckan.site_logo "/logo.png"
conf_set ckan.favicon "favicon.png"
#conf_set ckan.site_intro_text ""
conf_set ckan.site_about "
# About
#$(conf_get ckan.site_intro_text)

# Developers
Source code available at [gitlab.com/gisdev.io/catalogue-tools4msp](https://gitlab.com/gisdev.io/catalogue-tools4msp).
"

#ckanext-branding
conf_set_list ckan.plugins branding

#ckanext-schemas
conf_set_list ckan.plugins schemas
conf_set scheming.dataset_schemas "ckanext.schemas:custom_schema.yaml ckanext.schemas:msp_data.json ckanext.schemas:msp_portal.json ckanext.schemas:msp_tool.json"
#conf_set ckan.default.package_type "msp-data" # CKAN > 2.9
DOMAINAREAS_PATH="/usr/lib/ckan/domainareas.json"
wget -nv "$DOMAINAREAS_URL" -O "$DOMAINAREAS_PATH"
conf_set ckan.domainareas_path "$DOMAINAREAS_PATH"

#ckanext-scheming
conf_set_list ckan.plugins scheming_datasets
conf_set ckan.search.show_all_types true

#ckanext-spatial
conf_set_list ckan.plugins spatial_metadata spatial_query
conf_set ckanext.spatial.search_backend solr-bbox
conf_set ckan.solr_url "$CKAN_SOLR_URL"

#datapusher
conf_set_list ckan.plugins datastore datapusher
conf_set ckan.datapusher.callback_url_base "$CKAN_SITE_URL_INTERNAL"
ckan datastore set-permissions | psql "$CKAN_SQLALCHEMY_URL"
(sleep 1m && ckan datapusher submit -y) &

exec "$@"
