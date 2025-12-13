# Odoo 19 Installation and Testing Guide

**Date:** December 9, 2025  
**Odoo Version:** 19.0  
**Status:** ✅ Installed and Running

---

## 🎯 Quick Start

### 1. Start Odoo

```bash
cd property_fielder
docker-compose up -d
```

### 2. Access Odoo

Open your browser and navigate to:
- **URL:** http://localhost:8069
- **Admin Password:** admin (configured in odoo.conf)

### 3. Create Database

On first access, you'll see the database creation screen:
1. **Master Password:** admin
2. **Database Name:** property_fielder
3. **Email:** your-email@example.com
4. **Password:** Choose a strong password
5. **Language:** English
6. **Country:** United Kingdom (or your country)
7. **Demo Data:** ❌ Uncheck (we don't want demo data)

Click **Create Database**

---

## 📦 Docker Setup

### Services Running

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| **PostgreSQL 15** | property_fielder_db | 5433 | Database |
| **Odoo 19.0** | property_fielder_odoo | 8069 | Web Application |

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker logs property_fielder_odoo
docker logs property_fielder_db

# Restart Odoo
docker restart property_fielder_odoo

# Stop and remove everything (including volumes)
docker-compose down -v
```

---

## 🔧 Configuration

### Odoo Configuration (odoo.conf)

```ini
[options]
# Database
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
db_name = property_fielder

# Addons path - includes our custom addons
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons

# Server
http_port = 8069
longpolling_port = 8072

# Development mode
dev_mode = reload,qweb,werkzeug,xml
auto_reload = True
workers = 0

# Admin password
admin_passwd = admin
```

### Custom Addons Location

Our addons are mounted at:
- **Host:** `E:\dev\RoutingScheduling\property_fielder\addons`
- **Container:** `/mnt/extra-addons`

---

## 📋 Installing Property Fielder Addons

### Step 1: Update Apps List

1. Log in to Odoo (http://localhost:8069)
2. Go to **Apps** (top menu)
3. Click **Update Apps List** (top-right menu ⋮)
4. Click **Update** in the dialog

### Step 2: Remove Filters

In the Apps screen:
1. Click the search bar
2. Remove the "Apps" filter (click the ✕)
3. This will show all available modules

### Step 3: Install Addons (in order)

**Install in this order:**

#### 1. Property Fielder Field Service
- Search for: "Property Fielder Field Service"
- Click **Install**
- Wait for installation to complete

#### 2. Property Fielder Property Management
- Search for: "Property Fielder Property Management"
- Click **Install**
- Wait for installation to complete

#### 3. Property Fielder Field Service Mobile
- Search for: "Property Fielder Field Service Mobile"
- Click **Install**
- Wait for installation to complete

---

## ✅ Testing Checklist

### After Installing Each Addon

#### property_fielder_field_service
- [ ] No installation errors
- [ ] Menu appears in top bar
- [ ] Can create a Skill
- [ ] Can create an Inspector
- [ ] Can create a Job
- [ ] API endpoints accessible

#### property_fielder_property_management
- [ ] No installation errors
- [ ] Property Management menu appears
- [ ] Can create a Property
- [ ] Can view FLAGE+ certification types (7 types)
- [ ] Can create a certification
- [ ] Compliance dashboard loads

#### property_fielder_field_service_mobile
- [ ] No installation errors
- [ ] Mobile menu appears
- [ ] Mobile dashboard loads
- [ ] Can view jobs in mobile view

---

## 🐛 Troubleshooting

### Odoo won't start
```bash
# Check logs
docker logs property_fielder_odoo

# Restart container
docker restart property_fielder_odoo
```

### Database connection errors
```bash
# Check if database is running
docker ps | grep property_fielder_db

# Check database logs
docker logs property_fielder_db
```

### Addon not appearing
```bash
# Restart Odoo with update
docker restart property_fielder_odoo

# Or update module list in Odoo UI
Apps > Update Apps List
```

### Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "8070:8069"  # Change 8069 to 8070
```

---

## 📊 Next Steps

After successful installation:
1. ✅ Test each addon functionality
2. ✅ Document any errors or issues
3. ✅ Create test data
4. ✅ Verify all features work
5. ✅ Update documentation with findings

