#!/usr/bin/env python3
"""Test the job creation wizard"""

import xmlrpc.client

# Odoo connection details
url = 'http://localhost:8069'
db = 'property_fielder'
username = 'admin'
password = 'admin'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed")
    exit(1)

print(f"✅ Authenticated as user {uid}")

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Create wizard
print("\n📝 Creating wizard...")
wizard_id = models.execute_kw(db, uid, password,
    'property_fielder.create.jobs.wizard', 'create',
    [{
        'date_from': '2025-12-10',
        'date_to': '2026-01-10',
        'scheduled_date': '2025-12-15',
        'duration_minutes': 60,
        'priority': '1',  # '0'=Low, '1'=Normal, '2'=High, '3'=Urgent
    }])

print(f"✅ Wizard created with ID: {wizard_id}")

# Get first 5 properties
print("\n🔍 Getting properties...")
property_ids = models.execute_kw(db, uid, password,
    'property_fielder.property', 'search',
    [[]], {'limit': 5})

print(f"✅ Found {len(property_ids)} properties")

# Manually assign properties to wizard
print("\n📝 Assigning properties to wizard...")
models.execute_kw(db, uid, password,
    'property_fielder.create.jobs.wizard', 'write',
    [[wizard_id], {'property_ids': [(6, 0, property_ids)]}])

property_count = len(property_ids)
print(f"✅ Assigned {property_count} properties to wizard")

try:
    
    if property_count > 0:
        # Create jobs
        print("\n🚀 Creating jobs...")
        models.execute_kw(db, uid, password,
            'property_fielder.create.jobs.wizard', 'action_create_jobs',
            [[wizard_id]])
        
        # Count created jobs
        job_count = models.execute_kw(db, uid, password,
            'property_fielder.job', 'search_count',
            [[['property_id', '!=', False]]])
        
        print(f"✅ Created {job_count} jobs")
        
        # Show first 3 jobs
        job_ids = models.execute_kw(db, uid, password,
            'property_fielder.job', 'search',
            [[['property_id', '!=', False]]], {'limit': 3})
        
        jobs = models.execute_kw(db, uid, password,
            'property_fielder.job', 'read',
            [job_ids, ['job_number', 'name', 'property_id']])
        
        print("\n📋 Sample jobs:")
        for job in jobs:
            print(f"  - {job['job_number']}: {job['name']} at {job['property_id'][1]}")
    else:
        print("⚠️  No properties found in date range")
        
except Exception as e:
    print(f"❌ Error: {e}")

