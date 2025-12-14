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
print(f"export DB_HOST={url.hostname or 'db'}")
print(f"export DB_PORT={url.port or 5432}")
print(f"export DB_USER={url.username or 'odoo'}")
print(f"export DB_PASSWORD={url.password or 'odoo'}")
print(f"export DB_NAME={url.path.lstrip('/') or 'property_fielder'}")
EOF
)
else
    # Fallback to individual env vars
    export DB_HOST=${PGHOST:-db}
    export DB_PORT=${PGPORT:-5432}
    export DB_USER=${PGUSER:-odoo}
    export DB_PASSWORD=${PGPASSWORD:-odoo}
    export DB_NAME=${PGDATABASE:-property_fielder}
fi

# Admin password
ADMIN_PASSWD=${ODOO_ADMIN_PASSWORD:-admin}

echo "Connecting to database: $DB_HOST:$DB_PORT/$DB_NAME as user: $DB_USER"
echo "HTTP Port: $HTTP_PORT"

# Check if using postgres superuser - Odoo blocks this by default
if [ "$DB_USER" = "postgres" ]; then
    echo "WARNING: Using postgres superuser. Creating 'odoo' user..."
    # Try to create odoo user in PostgreSQL
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'odoo') THEN CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo' CREATEDB; END IF; END \$\$;" 2>/dev/null || true

    # Grant privileges on database
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO odoo;" 2>/dev/null || true
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "ALTER DATABASE $DB_NAME OWNER TO odoo;" 2>/dev/null || true

    # Grant privileges on schema and tables (for existing data)
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "GRANT ALL ON SCHEMA public TO odoo; GRANT ALL ON ALL TABLES IN SCHEMA public TO odoo; GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO odoo;" 2>/dev/null || true
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "ALTER SCHEMA public OWNER TO odoo;" 2>/dev/null || true

    # Switch to odoo user
    DB_USER="odoo"
    DB_PASSWORD="odoo"
    echo "Switched to user: $DB_USER"
fi

# Create runtime config with database settings
cat > /tmp/odoo-runtime.conf << EOF
[options]
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_name = $DB_NAME
http_port = $HTTP_PORT
http_interface = 0.0.0.0
admin_passwd = $ADMIN_PASSWD
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
proxy_mode = True
list_db = False
workers = 2
limit_time_cpu = 600
limit_time_real = 1200
log_level = info
EOF

# Check if database needs initialization
echo "Checking if database $DB_NAME needs initialization..."
DB_INITIALIZED=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_module_module');" 2>/dev/null || echo "false")

if [ "$DB_INITIALIZED" = "t" ]; then
    echo "Database is already initialized, starting Odoo normally..."
    INIT_FLAG=""
else
    echo "Database needs initialization, will initialize base module..."
    INIT_FLAG="-i base"
fi

# Start Odoo with runtime configuration
exec odoo --config=/tmp/odoo-runtime.conf --db-filter="^${DB_NAME}$" $INIT_FLAG

