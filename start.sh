#!/bin/bash
# Property Fielder - Odoo startup script for Railway
set -e

echo "Starting Property Fielder (Odoo 19)..."

# Use Railway's PORT or default to 8069
HTTP_PORT=${PORT:-8069}

# Parse DATABASE_URL using Python (more reliable than sed)
if [ -n "$DATABASE_URL" ]; then
    echo "Parsing DATABASE_URL..."
    eval $(python3 << EOF
import os
from urllib.parse import urlparse
url = urlparse(os.environ.get('DATABASE_URL', ''))
print(f"DB_HOST={url.hostname or 'db'}")
print(f"DB_PORT={url.port or 5432}")
print(f"DB_USER={url.username or 'odoo'}")
print(f"DB_PASSWORD={url.password or 'odoo'}")
print(f"DB_NAME={url.path.lstrip('/') or 'property_fielder'}")
EOF
)
else
    # Fallback to individual env vars
    DB_HOST=${PGHOST:-db}
    DB_PORT=${PGPORT:-5432}
    DB_USER=${PGUSER:-odoo}
    DB_PASSWORD=${PGPASSWORD:-odoo}
    DB_NAME=${PGDATABASE:-property_fielder}
fi

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

