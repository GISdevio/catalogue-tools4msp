#!/bin/bash
set -e

# This script runs from outside the container and creates .env file

# All informational messages go to stderr
echo "🚀 Initializing CKAN and getting credentials..." >&2

# Create admin user if not exists
echo "👤 Creating admin user..." >&2
docker compose exec -T ckan ckan -c /srv/app/ckan.ini user add admin \
    fullname="Admin User" \
    email="admin@example.com" \
    password="admin123" \
    2>/dev/null >&2 || echo "Admin user already exists" >&2

docker compose exec -T ckan ckan -c /srv/app/ckan.ini sysadmin add admin 2>/dev/null >&2

# Generate API key for admin user
echo "🔑 Generating API key..." >&2
API_KEY=$(docker compose exec -T ckan ckan -c /srv/app/ckan.ini user token add admin test-fixtures 2>/dev/null | awk 'NR>1 {print $1}')

if [ -z "$API_KEY" ]; then
    echo "❌ Could not generate API key" >&2
    exit 1
fi

echo "✅ Got API key: ${API_KEY:0:8}..." >&2

# Write .env file
echo "📝 Writing .env file..." >&2
cat > .env << EOF
CKAN_URL=http://localhost:5000
CKAN_API_KEY=$API_KEY
EOF

echo "✅ Credentials written to .env" >&2