#!/bin/bash
set -e

# Run the custom entrypoint first
/custom-entrypoint.sh

conf="/srv/app/ckan.ini"

# Enable debug mode for development
crudini --set "$conf" DEFAULT debug "true"

# Re-run uv sync to ensure editable installs are properly linked even with host mounts
uv sync --locked

# Extensions are already installed in editable mode via uv sync during build
exec "$@"
