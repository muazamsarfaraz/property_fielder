# Property Fielder - UK Property Inspection Platform

**Complete field service management with FLAGE+ certification tracking for UK property inspections**

**Version:** 3.0.0
**Status:** ✅ All Odoo Addons Complete | ✅ Flutter Mobile App Complete
**Platform:** Odoo 19.0 | Flutter 3.x

---

## 🎯 WHAT IS THIS?

A **complete property inspection platform** for UK property management companies, featuring:
- **FLAGE+ Certification Tracking** - Gas Safety, EPC, EICR, Fire Safety, Legionella, Asbestos
- **Field Service Management** - Jobs, routes, inspectors, optimization
- **Mobile Inspector App** - Flutter app with offline support
- **Route Optimization** - AI-powered scheduling with Timefold Solver

Perfect for:
- 🏠 UK Property Management Companies
- 🔧 Letting Agents and Landlords
- ⚡ Property Inspection Services
- 📋 Compliance and Certification Companies

---

## 📦 PROJECT STRUCTURE

```
property_fielder/
├── README.md                    # This file
├── docker-compose.yml           # Docker setup for Odoo 19 + PostgreSQL
├── odoo.conf                    # Odoo configuration
│
├── addons/                      # Odoo 19 addons
│   ├── property_fielder_field_service/        # Field service management
│   ├── property_fielder_property_management/  # FLAGE+ certifications
│   └── property_fielder_field_service_mobile/ # Mobile API endpoints
│
└── mobile_app/                  # Flutter mobile app
    ├── lib/                     # Dart source code
    └── pubspec.yaml             # Flutter dependencies
```

---

## 🚀 QUICK START

### 1. Docker Setup (Recommended)

```bash
cd property_fielder
docker-compose up -d
```

This starts:
- **Odoo 19** on http://localhost:8069
- **PostgreSQL 16** database

### 2. Install Addons

1. Go to http://localhost:8069
2. Create database: `property_fielder`
3. Go to Apps → Update Apps List
4. Install in order:
   - Property Fielder Property Management
   - Property Fielder Field Service
   - Property Fielder Field Service Mobile

### 3. Flutter Mobile App

```bash
cd mobile_app
flutter pub get
flutter pub run build_runner build
flutter run
```

---

## ✨ FEATURES

### Odoo Addons (Complete)

✅ **Property Management**
- FLAGE+ certification tracking (Gas, EPC, EICR, Fire, Legionella, Asbestos)
- Property portfolio management
- Compliance dashboard with expiry alerts
- Certification reports

✅ **Field Service**
- Job management with time windows
- Inspector management with skills
- Route optimization with Timefold Solver
- Interactive dispatch view (Map + Timeline)
- Schedule sharing via email
- Change request workflow

✅ **Mobile API**
- REST endpoints for mobile app
- Check-in/out tracking
- Photo upload with GPS
- Signature capture
- Notes and voice memos

### Flutter Mobile App (Complete)

✅ **Core Features**
- Offline-first architecture with Hive storage
- Background sync with conflict resolution
- GPS-based check-in/out
- Photo capture with GPS tagging
- Signature capture
- Notes with categories

✅ **Screens**
- Dashboard with job stats
- Job list with tabs (Today/Upcoming/Completed)
- Job detail with actions
- Route list with progress
- Photo gallery by category
- Signature capture pad
- Sync status screen
- Settings screen

---

## 🏗️ ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────────┐
│                    ODOO 19 PLATFORM                         │
│  • property_fielder_property_management (FLAGE+)            │
│  • property_fielder_field_service (Jobs, Routes)            │
│  • property_fielder_field_service_mobile (REST API)         │
└─────────────────────────────────────────────────────────────┘
                         ↓ REST API
┌─────────────────────────────────────────────────────────────┐
│              FLUTTER MOBILE APP                             │
│  • Offline storage (Hive)                                   │
│  • Background sync (WorkManager)                            │
│  • GPS tracking (Geolocator)                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 DOCUMENTATION

| Document | Purpose |
|----------|---------|
| [addons/README.md](addons/README.md) | Addon installation guide |
| [addons/ARCHITECTURE.md](addons/ARCHITECTURE.md) | System architecture |
| [mobile_app/README.md](mobile_app/README.md) | Flutter app guide |
| [ODOO_19_MIGRATION_GUIDE.md](ODOO_19_MIGRATION_GUIDE.md) | Odoo 19 migration patterns |
| [ODOO_INSTALLATION_GUIDE.md](ODOO_INSTALLATION_GUIDE.md) | Docker setup guide |

---

## 🛠️ DEVELOPMENT STATUS

### Completed ✅

- [x] Odoo 19 Docker setup
- [x] Property Management addon with FLAGE+ certifications
- [x] Field Service addon with dispatch view
- [x] Mobile API addon with REST endpoints
- [x] Flutter mobile app with offline support
- [x] All views, wizards, and workflows
- [x] Schedule sharing and change requests

---

**Last Updated:** December 10, 2025
**Version:** 3.0.0
**License:** LGPL-3.0

