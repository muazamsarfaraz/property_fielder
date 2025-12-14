# Property Fielder - Odoo 19 Dockerfile for Railway
FROM odoo:19.0

# Switch to root to install dependencies
USER root

# Install additional Python packages if needed
# Note: --break-system-packages required for Debian 12+ (Odoo 19 base image)
RUN pip3 install --no-cache-dir --break-system-packages requests

# Copy custom addons
COPY ./addons /mnt/extra-addons

# Copy Odoo configuration files
COPY ./odoo.conf /etc/odoo/odoo.conf
COPY ./odoo.prod.conf /etc/odoo/odoo.prod.conf

# Copy startup script
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo

# Switch back to odoo user
USER odoo

# Expose Odoo ports (Railway uses PORT env var)
EXPOSE 8069 8072

# Use startup script for production
CMD ["/start.sh"]

