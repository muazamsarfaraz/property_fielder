# Property Fielder Odoo 19 Addons

Custom addons for UK property compliance and field service management.

## Addons

| Addon | Technical Name | Purpose |
|-------|----------------|---------|
| Property Management | `property_fielder_property_management` | Properties, FLAGE+ certifications |
| Field Service | `property_fielder_field_service` | Jobs, routes, optimization |
| Mobile API | `property_fielder_field_service_mobile` | REST API for mobile app |

## Installation

1. Add this directory to `addons_path` in `odoo.conf`
2. Restart Odoo: `docker-compose restart`
3. Apps → Update Apps List
4. Install addons in order:
   - Property Fielder Property Management
   - Property Fielder Field Service
   - Property Fielder Field Service Mobile

## Testing

```bash
./odoo-bin -d test_db --test-enable --stop-after-init -i property_fielder_field_service
```

## License

LGPL-3.0

