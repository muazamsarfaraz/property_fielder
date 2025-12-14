#!/bin/bash
# Property Fielder - Odoo startup script for Railway
set -e

echo "Starting Property Fielder (Odoo 19)..."

# Railway provides DATABASE_URL or individual vars
# Parse DATABASE_URL if provided, otherwise use individual vars
if [ -n "$DATABASE_URL" ]; then
    # Parse postgres://user:password@host:port/dbname
    export DB_HOST=$(echo $DATABASE_URL | sed -E 's/.*@([^:]+):.*/\1/')
    export DB_PORT=$(echo $DATABASE_URL | sed -E 's/.*:([0-9]+)\/.*/\1/')
    export DB_USER=$(echo $DATABASE_URL | sed -E 's/postgres:\/\/([^:]+):.*/\1/')
    export DB_PASSWORD=$(echo $DATABASE_URL | sed -E 's/postgres:\/\/[^:]+:([^@]+)@.*/\1/')
    export DB_NAME=$(echo $DATABASE_URL | sed -E 's/.*\/([^?]+).*/\1/')
fi

# Use Railway's PORT or default to 8069
HTTP_PORT=${PORT:-8069}

# Database connection settings
DB_HOST=${DB_HOST:-${PGHOST:-db}}
DB_PORT=${DB_PORT:-${PGPORT:-5432}}
DB_USER=${DB_USER:-${PGUSER:-odoo}}
DB_PASSWORD=${DB_PASSWORD:-${PGPASSWORD:-odoo}}
DB_NAME=${DB_NAME:-${PGDATABASE:-property_fielder}}

# Admin password
ADMIN_PASSWD=${ODOO_ADMIN_PASSWORD:-admin}

echo "Connecting to database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "HTTP Port: $HTTP_PORT"

# Create runtime config with database settings
cat > /tmp/odoo-runtime.conf << EOF
[options]
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_name = $DB_NAME
http_port = $HTTP_PORT
admin_passwd = $ADMIN_PASSWD
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
proxy_mode = True
list_db = False
workers = 2
limit_time_cpu = 600
limit_time_real = 1200
log_level = info
EOF

# Start Odoo with runtime configuration
exec odoo --config=/tmp/odoo-runtime.conf

