# Odoo Addons - Field Service Management

This directory contains Odoo addons extracted from the routing & scheduling platform.

## 📦 Structure

```
addons/
├── property_fielder_field_service/     # Main Field Service addon for Odoo
│   ├── models/                  # Odoo models (Jobs, Inspectors, Routes)
│   ├── views/                   # XML views and UI
│   ├── controllers/             # HTTP controllers
│   ├── static/                  # JavaScript, CSS, images
│   ├── security/                # Access rights
│   ├── data/                    # Demo data
│   └── __manifest__.py          # Addon manifest
│
└── property_fielder_core/              # Shared utilities (optional base addon)
    ├── lib/                     # Python libraries
    │   ├── osrm_client.py       # OSRM API client
    │   ├── haversine.py         # Haversine distance calculator
    │   └── timefold_client.py   # Timefold Solver API client
    ├── models/                  # Shared models (Skills, Locations)
    └── __manifest__.py
```

## 🎯 Field Service Addon

**Module Name:** `property_fielder_field_service`  
**Purpose:** Job dispatch and route optimization for field service companies

**Features:**
- ✅ Job/visit management
- ✅ Inspector/technician scheduling
- ✅ Route optimization with Timefold Solver
- ✅ Real-time route visualization
- ✅ Skills-based job assignment
- ✅ Time window constraints
- ✅ Multi-day planning

**Dependencies:**
- Odoo 17.0+
- PostgreSQL 15+
- Python 3.10+
- External: Timefold Solver service (Quarkus)

## 🚀 Installation

### 1. Install Odoo
```bash
# Install Odoo 17
# See: https://www.odoo.com/documentation/17.0/administration/install.html
```

### 2. Copy Addon to Odoo
```bash
# Copy the addon to Odoo addons directory
cp -r addons/property_fielder_field_service /path/to/odoo/addons/

# Or add this directory to Odoo addons path
# In odoo.conf:
# addons_path = /path/to/odoo/addons,/path/to/property_fielder/addons
```

### 3. Update Apps List
```bash
# Restart Odoo with update flag
./odoo-bin -u all -d your_database
```

### 4. Install the Addon
- Go to Apps menu in Odoo
- Search for "Property Fielder Field Service"
- Click Install

## 🔧 Configuration

### Timefold Solver Service

The addon requires an external Timefold Solver service for route optimization.

**Option 1: Use existing Quarkus service**
```bash
# Start the vehicle routing service
cd services/vehicle-routing
mvn quarkus:dev
```

**Option 2: Deploy to Railway/Cloud**
```bash
# Deploy the Quarkus service to Railway
# See: services/vehicle-routing/README.MD
```

**Configure in Odoo:**
- Go to Settings → Technical → System Parameters
- Add parameter: `property_fielder.timefold.url` = `http://localhost:8080`

### OSRM Service (Optional)

For real road routing (optional - falls back to Haversine):

**Option 1: Use public OSRM**
- Set parameter: `property_fielder.osrm.url` = `https://router.project-osrm.org`

**Option 2: Deploy your own**
```bash
# Start OSRM service
cd services/osrm-service
docker-compose up
```
- Set parameter: `property_fielder.osrm.url` = `http://localhost:5000`

## 📚 Documentation

### Current System
- **Architecture:** `ARCHITECTURE.md` - System architecture overview
- **Complete Overview:** `COMPLETE_ADDON_OVERVIEW.md` - All current addons
- **Field Service Summary:** `FIELD_SERVICE_EXTRACTION_SUMMARY.md`
- **Mobile Summary:** `MOBILE_ADDON_SUMMARY.md`
- **Property Management Summary:** `PROPERTY_MANAGEMENT_SUMMARY.md`

### Future Development
- **📋 Development Roadmap:** `PROPERTY_MANAGEMENT_ROADMAP.md` - Complete 20-week implementation plan
- **📊 Quick Reference:** `ADDON_DEVELOPMENT_PLAN.md` - Quick reference for all planned addons
- **Custom Certifications Guide:** `property_fielder_property_management/CUSTOM_CERTIFICATIONS_GUIDE.md`

## 🧪 Testing

```bash
# Run Odoo tests
./odoo-bin -d test_db --test-enable --stop-after-init -i property_fielder_field_service
```

## 📄 License

See LICENSE file in root directory.

