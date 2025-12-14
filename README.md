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
│
├── e2e-tests/                   # Playwright E2E tests
├── mobile_app/                  # Flutter inspector app
├── docker-compose.yml           # Odoo 19 + PostgreSQL
└── odoo.conf                    # Odoo configuration
```

## Railway Deployment (Production)

**Auto-deploy**: Push to `master` branch triggers automatic deployment.

| Service | URL |
|---------|-----|
| **Property Fielder (Odoo)** | https://propertyfielder-production.up.railway.app |
| **Route Optimization (Timefold)** | https://job-dispatch.up.railway.app |
| **OSRM Routing (UK)** | https://osrmproj-production.up.railway.app |

### Deploy

```bash
git add .
git commit -m "Your changes"
git push origin master
# Railway auto-deploys in ~2-3 minutes
```

### Railway CLI

```bash
# Link project
railway link --project 1da4fd12-9fe3-4daa-aec7-33cd8e164098

# View logs
railway logs --lines 100

# Check status
railway status
```

## Local Development

```bash
docker-compose up -d
# Access: http://localhost:8069
# Install addons via Apps menu
```

**Note**: Local dev uses external Railway APIs for Timefold and OSRM.

## Implemented Addons

| Addon | Purpose | Status |
|-------|---------|--------|
| `property_fielder_property_management` | Properties, FLAGE+ certifications | ✅ Built |
| `property_fielder_field_service` | Jobs, Routes, Dispatch, Optimization | ✅ Built |
| `property_fielder_field_service_mobile` | Mobile REST API | ✅ Built |

## External Services

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Timefold | `POST /api/multi-day-plan` | Route optimization |
| Timefold | `GET /api/multi-day-plan/{id}` | Get optimization result |
| OSRM | `GET /route/v1/driving/{coords}` | Driving directions |
| OSRM | `GET /table/v1/driving/{coords}` | Distance matrix |

## PRD Documentation

See `prd/PRD_MAIN.md` for complete requirements.

**License:** LGPL-3.0

