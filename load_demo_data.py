#!/usr/bin/env python3
"""
Load demo data for Property Fielder Field Service addon.
This script manually loads the demo data XML file.
"""

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
    print("❌ Authentication failed!")
    exit(1)

print(f"✅ Authenticated as user ID: {uid}")

# Create XML-RPC object proxy
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Load the demo data XML file
print("\n📦 Loading demo data...")

try:
    # Use the ir.model.data load method to load XML data
    result = models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_install',
        [[models.execute_kw(db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'property_fielder_field_service']]]
        )[0]]]
    )
    
    print("✅ Demo data loaded successfully!")
    
    # Verify the data was loaded
    property_count = models.execute_kw(db, uid, password,
        'property_fielder.property', 'search_count',
        [[]]
    )
    
    inspector_count = models.execute_kw(db, uid, password,
        'res.partner', 'search_count',
        [[['name', 'in', ['Alice Johnson', 'Bob Smith', 'Carol Davis']]]]
    )
    
    print(f"\n📊 Data Summary:")
    print(f"   Properties: {property_count}")
    print(f"   Inspectors: {inspector_count}")
    
    if property_count == 50 and inspector_count == 3:
        print("\n🎉 SUCCESS! All 50 properties and 3 inspectors loaded!")
    else:
        print(f"\n⚠️  Expected 50 properties and 3 inspectors, but got {property_count} properties and {inspector_count} inspectors")
        
except Exception as e:
    print(f"❌ Error loading demo data: {e}")
    import traceback
    traceback.print_exc()

