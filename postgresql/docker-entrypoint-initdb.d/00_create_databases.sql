-- Create the main CKAN database
CREATE DATABASE ckan OWNER postgres ENCODING 'utf-8';

-- Create the DataStore database
CREATE DATABASE datastore OWNER postgres ENCODING 'utf-8';

-- Create CKAN user
CREATE USER ckan WITH PASSWORD 'ckan';

-- Create DataStore read-only user
CREATE USER datastore_ro WITH PASSWORD 'datastore';

-- Grant permissions to CKAN user
GRANT ALL PRIVILEGES ON DATABASE ckan TO ckan;
GRANT ALL PRIVILEGES ON DATABASE datastore TO ckan;

-- Grant schema permissions (PostgreSQL 15 requirement)
\c ckan
GRANT ALL ON SCHEMA public TO ckan;
\c datastore
GRANT ALL ON SCHEMA public TO ckan;

-- Grant read-only permissions to DataStore user
GRANT CONNECT ON DATABASE datastore TO datastore_ro;
GRANT USAGE ON SCHEMA public TO datastore_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO datastore_ro;