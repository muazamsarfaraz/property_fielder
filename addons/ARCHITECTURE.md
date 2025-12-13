# Field Service Addon - Architecture

**Date:** December 9, 2025

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                         ODOO PLATFORM                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Property Fielder Field Service Addon                            │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │   Models     │  │ Controllers  │  │    Views     │   │ │
│  │  │              │  │              │  │              │   │ │
│  │  │ • Job        │  │ • REST API   │  │ • Forms      │   │ │
│  │  │ • Inspector  │  │ • Distance   │  │ • Lists      │   │ │
│  │  │ • Route      │  │ • Optimize   │  │ • Maps       │   │ │
│  │  │ • Skill      │  │              │  │ • Dashboard  │   │ │
│  │  │ • Optimize   │  │              │  │              │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │ │
│  │                                                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  PostgreSQL Database                                            │
│  • Jobs, Inspectors, Routes, Skills, Optimizations             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP API
┌─────────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES (Microservices)                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Timefold Solver Service (Quarkus)                        │ │
│  │  • Vehicle routing optimization                           │ │
│  │  • Constraint satisfaction                                │ │
│  │  • Multi-day planning                                     │ │
│  │  Port: 8080                                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  OSRM Service (Optional)                                  │ │
│  │  • Real road routing                                      │ │
│  │  • Distance calculations                                  │ │
│  │  • Route geometry                                         │ │
│  │  Port: 5000                                               │ │
│  │  Fallback: Haversine (built-in)                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 DATA FLOW

### **1. Job Creation Flow**

```
User → Odoo UI → Job Model → PostgreSQL
                    ↓
              Validation
                    ↓
              Save to DB
                    ↓
              Return Job ID
```

### **2. Route Optimization Flow**

```
User clicks "Optimize Routes"
         ↓
Optimization Model
         ↓
Build Timefold Request
  • Jobs → Visits
  • Inspectors → Vehicles
  • Config → Settings
         ↓
HTTP POST → Timefold Service
         ↓
Timefold Solver runs (30s)
  • Constraint satisfaction
  • Route optimization
  • Skills matching
         ↓
Return optimized solution
         ↓
Process Response
  • Create Route records
  • Assign Jobs to Routes
  • Update Job status
         ↓
Display Results to User
```

### **3. Distance Calculation Flow**

```
Need distance between A and B
         ↓
Check: Use OSRM?
         ↓
    YES ─────────────────┐
         ↓               ↓
    HTTP GET → OSRM     Fallback
         ↓               ↓
    Success?        Haversine
         ↓               ↓
    Return distance ────┘
         ↓
    Use in optimization
```

---

## 🔄 INTEGRATION PATTERNS

### **Pattern 1: Synchronous API Call**

Used for: Distance calculations, quick queries

```python
# Odoo Controller
response = requests.get(f'{osrm_url}/route/...')
if response.status_code == 200:
    return response.json()
else:
    # Fallback to Haversine
    return calculate_haversine(...)
```

### **Pattern 2: Asynchronous Optimization**

Used for: Route optimization (long-running)

```python
# Odoo Model
def action_run_optimization(self):
    self.state = 'running'
    
    # Call Timefold (blocks for 30s)
    response = requests.post(
        f'{timefold_url}/route-plans',
        json=request_data,
        timeout=60
    )
    
    # Process results
    self._process_response(response.json())
    self.state = 'completed'
```

**Future Enhancement:** Use Odoo queue_job for true async

### **Pattern 3: Fallback Strategy**

Used for: OSRM integration

```python
try:
    # Try OSRM
    result = call_osrm(...)
except Exception:
    # Fallback to Haversine
    result = calculate_haversine(...)
```

---

## 🗄️ DATABASE SCHEMA

### **Core Tables**

```sql
-- Skills
property_fielder_skill
  - id (PK)
  - name
  - code (UNIQUE)
  - description
  - active
  - color

-- Jobs
property_fielder_job
  - id (PK)
  - job_number (UNIQUE)
  - name
  - partner_id (FK → res_partner)
  - latitude, longitude
  - scheduled_date
  - earliest_start, latest_end
  - duration_minutes
  - priority
  - inspector_id (FK → property_fielder_inspector)
  - route_id (FK → property_fielder_route)
  - state

-- Inspectors
property_fielder_inspector
  - id (PK)
  - name
  - employee_id (FK → hr_employee)
  - user_id (FK → res_users)
  - home_latitude, home_longitude
  - shift_start, shift_end
  - max_jobs_per_day
  - vehicle_capacity
  - active

-- Routes
property_fielder_route
  - id (PK)
  - route_number (UNIQUE)
  - name
  - inspector_id (FK → property_fielder_inspector)
  - route_date
  - total_distance_km
  - total_drive_time_minutes
  - total_work_time_minutes
  - optimization_id (FK → property_fielder_optimization)
  - optimization_score
  - route_geometry (GeoJSON)
  - state

-- Optimizations
property_fielder_optimization
  - id (PK)
  - name
  - optimization_date
  - use_osrm
  - solver_time_seconds
  - score
  - state
  - request_json
  - response_json
  - error_message

-- Many2Many Relations
job_skill_rel (job_id, skill_id)
inspector_skill_rel (inspector_id, skill_id)
optimization_job_rel (optimization_id, job_id)
optimization_inspector_rel (optimization_id, inspector_id)
```

---

## 🔌 API ENDPOINTS

### **Odoo REST API** (JSON-RPC)

```
GET  /Property Fielder/api/jobs
     ?date=2025-12-09
     &inspector_id=5

GET  /Property Fielder/api/routes
     ?date=2025-12-09
     &inspector_id=5

POST /Property Fielder/api/optimize
     {
       "job_ids": [1, 2, 3],
       "inspector_ids": [1, 2],
       "date": "2025-12-09",
       "use_osrm": false,
       "solver_time": 30
     }

POST /Property Fielder/api/distance
     {
       "from_lat": 51.5074,
       "from_lon": -0.1278,
       "to_lat": 51.5155,
       "to_lon": -0.0922,
       "use_osrm": false
     }
```

### **Timefold API** (External Service)

```
POST http://localhost:8080/route-plans
     {
       "name": "Route Optimization",
       "visits": [...],
       "vehicles": [...],
       "useOsrmRouting": false,
       "solverTimeSeconds": 30
     }

Response:
     {
       "score": "0hard/-12345soft",
       "routes": [...]
     }
```

### **OSRM API** (External Service)

```
GET http://localhost:5000/route/v1/driving/{lon1},{lat1};{lon2},{lat2}
    ?overview=false

Response:
    {
      "code": "Ok",
      "routes": [{
        "distance": 1234.5,
        "duration": 567.8
      }]
    }
```

---

## 🎨 FRONTEND ARCHITECTURE

### **Odoo OWL Components** (To Be Built)

```
MapWidget
  • Leaflet.js integration
  • Display jobs as markers
  • Display routes as polylines
  • Click handlers for jobs/routes

TimelineWidget
  • Vis-Timeline integration
  • Show inspector schedules
  • Show job time windows
  • Drag-and-drop support

RouteOptimizerWidget
  • Configuration form
  • Progress indicator
  • Results display
  • Action buttons

DashboardWidget
  • KPI cards
  • Charts (jobs, routes, distance)
  • Quick actions
```

---

## 🔐 SECURITY ARCHITECTURE

### **Access Control Layers**

1. **User Authentication** - Odoo login
2. **Group-Based Access** - User vs Manager
3. **Record Rules** - Company-level filtering
4. **Field-Level Security** - Sensitive fields
5. **API Authentication** - JSON-RPC session

### **External Service Security**

- Timefold: Internal network only (no auth)
- OSRM: Public or internal (no auth)
- Future: Add API keys for production

---

**This architecture supports:**
- ✅ Scalability (separate services)
- ✅ Flexibility (optional OSRM)
- ✅ Maintainability (clean separation)
- ✅ Extensibility (easy to add features)

