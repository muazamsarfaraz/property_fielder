#!/usr/bin/env python3
"""Run optimization with varied certificate durations"""
import xmlrpc.client
import json
import time
from datetime import date

url = 'http://localhost:8069'
db = 'property_fielder'
username = 'admin'
password = 'admin'

# Connect
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Show certification type durations
print("=== CERTIFICATION TYPE DURATIONS ===")
cert_types = models.execute_kw(db, uid, password, 'property_fielder.certification.type', 'search_read',
    [[]], {'fields': ['id', 'name', 'code', 'default_duration_minutes'], 'order': 'sequence'})
cert_dur_map = {ct['code']: ct['default_duration_minutes'] for ct in cert_types}
for ct in cert_types:
    print(f"  {ct['code']:15} {ct['name']:45} {ct['default_duration_minutes']:3} min")

# Update existing jobs with correct durations from their inspection's cert type
print("\n=== UPDATING EXISTING JOB DURATIONS ===")
inspections = models.execute_kw(db, uid, password, 'property_fielder.property.inspection', 'search_read',
    [[['job_id', '!=', False]]], {'fields': ['job_id', 'certification_type_id']})
for insp in inspections:
    if insp['job_id'] and insp['certification_type_id']:
        job_id = insp['job_id'][0]
        cert_type_id = insp['certification_type_id'][0]
        # Get the cert type's duration
        ct = models.execute_kw(db, uid, password, 'property_fielder.certification.type', 'read',
            [[cert_type_id], ['code', 'default_duration_minutes']])[0]
        dur = ct['default_duration_minutes']
        # Update job
        models.execute_kw(db, uid, password, 'property_fielder.job', 'write',
            [[job_id], {'duration_minutes': dur}])
        print(f"  Job {job_id}: updated to {dur} min ({ct['code']})")

# Create varied test jobs with different certificate types
print("\n=== CREATING VARIED TEST JOBS ===")
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
earliest = f"{today} 08:00:00"
latest = f"{today} 18:00:00"

# Get certificate types
cert_types = {ct['code']: ct for ct in models.execute_kw(db, uid, password,
    'property_fielder.certification.type', 'search_read', [[]],
    {'fields': ['id', 'code', 'name', 'default_duration_minutes']})}

# Create test jobs with different certificate types
test_jobs = [
    ('Gas Safety Check - London N1', 'GAS', 51.5387, -0.0987),
    ('EICR Test - London E1', 'ELECTRICAL', 51.5165, -0.0626),
    ('EPC Assessment - London W1', 'EPC', 51.5132, -0.1503),
    ('Fire Risk Assessment - London SE1', 'FIRE', 51.4951, -0.0775),
    ('PAT Testing - London EC1', 'PAT', 51.5185, -0.0987),
    ('Legionella Survey - London NW1', 'LEGIONELLA', 51.5298, -0.1365),
]

# Get default partner and UK country
partner_ids = models.execute_kw(db, uid, password, 'res.partner', 'search', [[]], {'limit': 1})
partner_id = partner_ids[0] if partner_ids else False
uk_ids = models.execute_kw(db, uid, password, 'res.country', 'search', [[['code', '=', 'GB']]])
uk_id = uk_ids[0] if uk_ids else False

for name, cert_code, lat, lng in test_jobs:
    ct = cert_types.get(cert_code)
    if not ct:
        continue
    job_id = models.execute_kw(db, uid, password, 'property_fielder.job', 'create', [{
        'name': name,
        'partner_id': partner_id,
        'street': name.split(' - ')[1] if ' - ' in name else 'London',
        'city': 'London',
        'country_id': uk_id,
        'latitude': lat,
        'longitude': lng,
        'scheduled_date': today,
        'earliest_start': earliest,
        'latest_end': latest,
        'duration_minutes': ct['default_duration_minutes'],
        'state': 'draft',
    }])
    print(f"  Created Job {job_id}: {name} ({ct['default_duration_minutes']} min)")

# Find draft jobs
job_ids = models.execute_kw(db, uid, password, 'property_fielder.job', 'search',
    [[['state', '=', 'draft']]], {'limit': 12})
print(f"\nFound {len(job_ids)} draft jobs")

# Show job durations
jobs = models.execute_kw(db, uid, password, 'property_fielder.job', 'read',
    [job_ids, ['name', 'duration_minutes']])
print("\n=== JOB DURATIONS ===")
for j in jobs:
    print(f"  {j['name']:55} {j['duration_minutes']:3} min")

# Find inspectors
insp_ids = models.execute_kw(db, uid, password, 'property_fielder.inspector', 'search', [[]])
print(f"\nFound {len(insp_ids)} inspectors")

if job_ids and insp_ids:
    today = date.today().isoformat()
    print(f"\n=== RUNNING OPTIMIZATION ===")
    result = models.execute_kw(db, uid, password, 'property_fielder.optimization', 'run_optimization',
        [job_ids, insp_ids, today])
    print(f"Started: {result}")

    # Wait for completion
    print("Waiting for optimization...")
    time.sleep(15)

    # Get optimization
    opt_id = result.get('optimization_id') if isinstance(result, dict) else None
    if not opt_id:
        opt_ids = models.execute_kw(db, uid, password, 'property_fielder.optimization', 'search',
            [[]], {'order': 'id desc', 'limit': 1})
        opt_id = opt_ids[0] if opt_ids else None

    opt = models.execute_kw(db, uid, password, 'property_fielder.optimization', 'read',
        [[opt_id], ['state', 'score', 'request_json', 'response_json']])[0]
    print(f"\nState: {opt['state']}, Score: {opt['score']}")

    # Check request durations
    req = json.loads(opt['request_json']) if opt.get('request_json') else {}
    if req.get('visits'):
        print('\n=== REQUEST - SERVICE DURATIONS ===')
        for v in req['visits']:
            ms = v.get('serviceDuration', 0)
            print(f"  Visit {v['id']}: {ms}ms = {ms/60000:.0f} min")

    # Check response schedule
    resp = json.loads(opt['response_json']) if opt.get('response_json') else {}
    print('\n=== RESPONSE - SCHEDULED TIMES ===')
    for vehicle in resp.get('vehicles', []):
        visits = vehicle.get('visits', [])
        if not visits:
            continue
        print(f"\nVehicle {vehicle['id']} ({len(visits)} visits):")
        for vid in visits:
            vd = next((v for v in resp.get('visits', []) if str(v.get('id')) == str(vid)), None)
            if vd:
                arr = vd.get('arrivalTime', 'N/A')[11:19] if vd.get('arrivalTime') else 'N/A'
                dep = vd.get('departureTime', 'N/A')[11:19] if vd.get('departureTime') else 'N/A'
                svc_min = vd.get('serviceDuration', 0) / 60000
                print(f"  Visit {vid}: arrive {arr} → depart {dep} ({svc_min:.0f} min service)")
else:
    print("No jobs or inspectors found")
