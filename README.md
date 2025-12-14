# Property Fielder - UK Property Compliance Platform

Odoo 19 addons for UK property compliance and field service management.

## Project Structure

```text
property_fielder/
├── addons/                      # Odoo 19 addons
│   ├── property_fielder_field_service/        # Core: Jobs, Routes, Optimization
│   ├── property_fielder_field_service_mobile/ # Core: Mobile API
│   └── property_fielder_property_management/  # Core: Properties, FLAGE+ Certs
│
├── prd/                         # Product Requirements Documents
│   ├── PRD_MAIN.md              # Master PRD (all requirements)
│   └── addons/                  # Per-addon PRDs
│       ├── core/                # Core addons (3)
│       ├── compliance/          # Compliance addons (5)
│       └── property_management/ # Business addons (14)
│
├── e2e-tests/                   # Playwright E2E tests
├── mobile_app/                  # Flutter inspector app
├── docker-compose.yml           # Odoo 19 + PostgreSQL
└── odoo.conf                    # Odoo configuration
```

## Quick Start

```bash
docker-compose up -d
# Access: http://localhost:8069
# Install addons via Apps menu
```

## Implemented Addons

| Addon | Purpose | Status |
|-------|---------|--------|
| `property_fielder_property_management` | Properties, FLAGE+ certifications | ✅ Built |
| `property_fielder_field_service` | Jobs, Routes, Dispatch, Optimization | ✅ Built |
| `property_fielder_field_service_mobile` | Mobile REST API | ✅ Built |

## PRD Documentation

See `prd/PRD_MAIN.md` for complete requirements. Individual addon PRDs in `prd/addons/`.

**License:** LGPL-3.0

