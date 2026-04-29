#!/bin/bash
set -e

# CKAN 2.11 doesn't have a standard entrypoint, we'll configure directly
echo "Configuring CKAN 2.11..."


conf="/srv/app/ckan.ini"

# Generate config if it doesn't exist
if [ ! -f "$conf" ]; then
    echo "Generating CKAN config file..."
    mkdir -p "$(dirname "$conf")"
    ckan generate config "$conf"
fi

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
conf_set ckan.plugins "image_view text_view datatables_view"
conf_set debug "false"
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
DOMAINAREAS_PATH="/var/lib/ckan/domainareas.json"
if wget -nv "$DOMAINAREAS_URL" -O "$DOMAINAREAS_PATH" 2>/dev/null; then
    conf_set ckan.domainareas_path "$DOMAINAREAS_PATH"
    echo "Downloaded domain areas to $DOMAINAREAS_PATH"
else
    echo "Warning: Could not download domain areas from $DOMAINAREAS_URL"
fi

#ckanext-scheming
conf_set_list ckan.plugins scheming_datasets
conf_set ckan.search.show_all_types true

#ckanext-spatial
conf_set_list ckan.plugins spatial_metadata spatial_query
conf_set ckanext.spatial.search_backend solr-bbox
conf_set ckan.solr_url "$CKAN_SOLR_URL"

#xloader
conf_set_list ckan.plugins datastore xloader
# Datastore permissions will be set when database is ready

exec "$@"
