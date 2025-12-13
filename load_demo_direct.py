#!/usr/bin/env python3
"""
Direct demo data loader using Odoo ORM.
This script creates the demo data records directly using the Odoo API.
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

# Get UK country ID
uk_id = models.execute_kw(db, uid, password,
    'res.country', 'search',
    [[['code', '=', 'GB']]]
)[0]

print(f"\n📦 Creating demo data...")
print(f"   UK Country ID: {uk_id}")

# Create 3 inspectors
inspectors_data = [
    {
        'name': 'Alice Johnson',
        'company_type': 'person',
        'street': 'Central London',
        'city': 'London',
        'zip': 'SW1A 1AA',
        'country_id': uk_id,
        'phone': '+44 20 7123 4567',
        'email': 'alice.johnson@fielder.one',
        'is_company': False,
    },
    {
        'name': 'Bob Smith',
        'company_type': 'person',
        'street': 'East London',
        'city': 'London',
        'zip': 'E1 6AN',
        'country_id': uk_id,
        'phone': '+44 20 7123 4568',
        'email': 'bob.smith@fielder.one',
        'is_company': False,
    },
    {
        'name': 'Carol Davis',
        'company_type': 'person',
        'street': 'West London',
        'city': 'London',
        'zip': 'W1A 1AA',
        'country_id': uk_id,
        'phone': '+44 20 7123 4569',
        'email': 'carol.davis@fielder.one',
        'is_company': False,
    },
]

print("\n👥 Creating 3 inspectors...")
inspector_ids = []
for inspector_data in inspectors_data:
    inspector_id = models.execute_kw(db, uid, password,
        'res.partner', 'create',
        [inspector_data]
    )
    inspector_ids.append(inspector_id)
    print(f"   ✅ Created: {inspector_data['name']} (ID: {inspector_id})")

print(f"\n✅ Created {len(inspector_ids)} inspectors")

# Create 50 properties across London
# Valid property types: house, flat, bungalow, maisonette, commercial, other
properties_data = [
    # Central London (1-10)
    {'name': 'Camden Office Building', 'type': 'commercial', 'street': '123 Camden High Street', 'city': 'London', 'zip': 'NW1 7JR', 'lat': 51.5390, 'lng': -0.1426},
    {'name': 'Islington Residential Complex', 'type': 'flat', 'street': '456 Upper Street', 'city': 'London', 'zip': 'N1 0QH', 'lat': 51.5416, 'lng': -0.1030},
    {'name': 'Westminster Government Building', 'type': 'commercial', 'street': '789 Victoria Street', 'city': 'London', 'zip': 'SW1E 5NE', 'lat': 51.4975, 'lng': -0.1357},
    {'name': 'Shoreditch Tech Hub', 'type': 'commercial', 'street': '321 Old Street', 'city': 'London', 'zip': 'EC1V 9HU', 'lat': 51.5254, 'lng': -0.0863},
    {'name': 'Kensington Luxury Apartments', 'type': 'flat', 'street': '654 Kensington High Street', 'city': 'London', 'zip': 'W8 5SE', 'lat': 51.4991, 'lng': -0.1938},
    {'name': 'Canary Wharf Tower', 'type': 'commercial', 'street': '987 Canada Square', 'city': 'London', 'zip': 'E14 5AB', 'lat': 51.5054, 'lng': -0.0235},
    {'name': 'Hackney Community Center', 'type': 'commercial', 'street': '147 Mare Street', 'city': 'London', 'zip': 'E8 3RH', 'lat': 51.5450, 'lng': -0.0553},
    {'name': 'Chelsea Medical Clinic', 'type': 'commercial', 'street': '258 Kings Road', 'city': 'London', 'zip': 'SW3 5UL', 'lat': 51.4877, 'lng': -0.1700},
    {'name': 'Greenwich Warehouse', 'type': 'commercial', 'street': '369 Creek Road', 'city': 'London', 'zip': 'SE10 9SW', 'lat': 51.4826, 'lng': -0.0077},
    {'name': 'Hammersmith Office Park', 'type': 'commercial', 'street': '741 King Street', 'city': 'London', 'zip': 'W6 9NH', 'lat': 51.4927, 'lng': -0.2339},

    # North London (11-20)
    {'name': 'Finchley Family House', 'type': 'house', 'street': '12 Ballards Lane', 'city': 'London', 'zip': 'N3 1BJ', 'lat': 51.5988, 'lng': -0.1789},
    {'name': 'Barnet Bungalow', 'type': 'bungalow', 'street': '34 High Street', 'city': 'London', 'zip': 'EN5 5XQ', 'lat': 51.6538, 'lng': -0.2008},
    {'name': 'Enfield Estate', 'type': 'flat', 'street': '56 Church Street', 'city': 'London', 'zip': 'EN2 6AX', 'lat': 51.6523, 'lng': -0.0808},
    {'name': 'Tottenham Retail Park', 'type': 'commercial', 'street': '78 High Road', 'city': 'London', 'zip': 'N17 6QA', 'lat': 51.5885, 'lng': -0.0707},
    {'name': 'Wood Green Shopping Centre', 'type': 'commercial', 'street': '90 High Road', 'city': 'London', 'zip': 'N22 6YD', 'lat': 51.5975, 'lng': -0.1097},
    {'name': 'Muswell Hill Maisonette', 'type': 'maisonette', 'street': '23 Broadway', 'city': 'London', 'zip': 'N10 3HA', 'lat': 51.5900, 'lng': -0.1436},
    {'name': 'Crouch End Apartments', 'type': 'flat', 'street': '45 Park Road', 'city': 'London', 'zip': 'N8 8TE', 'lat': 51.5778, 'lng': -0.1197},
    {'name': 'Highgate Village House', 'type': 'house', 'street': '67 High Street', 'city': 'London', 'zip': 'N6 5JX', 'lat': 51.5717, 'lng': -0.1467},
    {'name': 'Archway Business Centre', 'type': 'commercial', 'street': '89 Junction Road', 'city': 'London', 'zip': 'N19 5QT', 'lat': 51.5656, 'lng': -0.1378},
    {'name': 'Holloway Flats', 'type': 'flat', 'street': '101 Holloway Road', 'city': 'London', 'zip': 'N7 8LT', 'lat': 51.5527, 'lng': -0.1197},

    # East London (21-30)
    {'name': 'Stratford Olympic Village', 'type': 'flat', 'street': '12 Olympic Way', 'city': 'London', 'zip': 'E20 1DY', 'lat': 51.5434, 'lng': 0.0139},
    {'name': 'Bow Commercial Hub', 'type': 'commercial', 'street': '34 Bow Road', 'city': 'London', 'zip': 'E3 2AD', 'lat': 51.5273, 'lng': -0.0245},
    {'name': 'Bethnal Green Terrace', 'type': 'house', 'street': '56 Roman Road', 'city': 'London', 'zip': 'E2 0RY', 'lat': 51.5267, 'lng': -0.0553},
    {'name': 'Mile End Apartments', 'type': 'flat', 'street': '78 Mile End Road', 'city': 'London', 'zip': 'E1 4UJ', 'lat': 51.5253, 'lng': -0.0333},
    {'name': 'Whitechapel Medical Centre', 'type': 'commercial', 'street': '90 Whitechapel Road', 'city': 'London', 'zip': 'E1 1BJ', 'lat': 51.5195, 'lng': -0.0601},
    {'name': 'Poplar Riverside Flats', 'type': 'flat', 'street': '12 East India Dock Road', 'city': 'London', 'zip': 'E14 0JJ', 'lat': 51.5089, 'lng': -0.0089},
    {'name': 'Limehouse Marina House', 'type': 'house', 'street': '34 Narrow Street', 'city': 'London', 'zip': 'E14 8DH', 'lat': 51.5117, 'lng': -0.0356},
    {'name': 'Wapping Warehouse Conversion', 'type': 'flat', 'street': '56 Wapping High Street', 'city': 'London', 'zip': 'E1W 2PN', 'lat': 51.5045, 'lng': -0.0589},
    {'name': 'Docklands Business Park', 'type': 'commercial', 'street': '78 Marsh Wall', 'city': 'London', 'zip': 'E14 9TP', 'lat': 51.5001, 'lng': -0.0189},
    {'name': 'Canning Town Flats', 'type': 'flat', 'street': '90 Barking Road', 'city': 'London', 'zip': 'E16 4HB', 'lat': 51.5145, 'lng': 0.0089},

    # South London (31-40)
    {'name': 'Brixton Market Building', 'type': 'commercial', 'street': '12 Electric Avenue', 'city': 'London', 'zip': 'SW9 8JX', 'lat': 51.4617, 'lng': -0.1145},
    {'name': 'Clapham Common House', 'type': 'house', 'street': '34 Clapham Common South Side', 'city': 'London', 'zip': 'SW4 7AB', 'lat': 51.4556, 'lng': -0.1378},
    {'name': 'Battersea Park Apartments', 'type': 'flat', 'street': '56 Prince of Wales Drive', 'city': 'London', 'zip': 'SW11 4NJ', 'lat': 51.4778, 'lng': -0.1556},
    {'name': 'Wandsworth Town House', 'type': 'house', 'street': '78 Old York Road', 'city': 'London', 'zip': 'SW18 1TG', 'lat': 51.4589, 'lng': -0.1889},
    {'name': 'Tooting Broadway Centre', 'type': 'commercial', 'street': '90 Tooting High Street', 'city': 'London', 'zip': 'SW17 0RN', 'lat': 51.4278, 'lng': -0.1678},
    {'name': 'Streatham Hill Maisonette', 'type': 'maisonette', 'street': '12 Streatham Hill', 'city': 'London', 'zip': 'SW2 4AH', 'lat': 51.4445, 'lng': -0.1256},
    {'name': 'Dulwich Village House', 'type': 'house', 'street': '34 Court Lane', 'city': 'London', 'zip': 'SE21 7EA', 'lat': 51.4445, 'lng': -0.0856},
    {'name': 'Peckham Rye Flats', 'type': 'flat', 'street': '56 Rye Lane', 'city': 'London', 'zip': 'SE15 4NB', 'lat': 51.4734, 'lng': -0.0689},
    {'name': 'Camberwell Business Centre', 'type': 'commercial', 'street': '78 Camberwell Road', 'city': 'London', 'zip': 'SE5 0EG', 'lat': 51.4834, 'lng': -0.0889},
    {'name': 'Elephant & Castle Tower', 'type': 'flat', 'street': '90 New Kent Road', 'city': 'London', 'zip': 'SE1 6TU', 'lat': 51.4945, 'lng': -0.0989},

    # West London (41-50)
    {'name': 'Notting Hill Townhouse', 'type': 'house', 'street': '12 Portobello Road', 'city': 'London', 'zip': 'W11 2DY', 'lat': 51.5156, 'lng': -0.2056},
    {'name': 'Shepherds Bush Centre', 'type': 'commercial', 'street': '34 Uxbridge Road', 'city': 'London', 'zip': 'W12 8LH', 'lat': 51.5045, 'lng': -0.2245},
    {'name': 'Acton Garden Flat', 'type': 'flat', 'street': '56 High Street', 'city': 'London', 'zip': 'W3 6RE', 'lat': 51.5089, 'lng': -0.2689},
    {'name': 'Ealing Broadway Plaza', 'type': 'commercial', 'street': '78 The Broadway', 'city': 'London', 'zip': 'W5 2NH', 'lat': 51.5145, 'lng': -0.3045},
    {'name': 'Chiswick Riverside House', 'type': 'house', 'street': '90 Chiswick High Road', 'city': 'London', 'zip': 'W4 1SH', 'lat': 51.4945, 'lng': -0.2656},
    {'name': 'Richmond Hill Bungalow', 'type': 'bungalow', 'street': '12 Hill Street', 'city': 'London', 'zip': 'TW10 6UA', 'lat': 51.4556, 'lng': -0.3045},
    {'name': 'Twickenham Stadium Flats', 'type': 'flat', 'street': '34 Rugby Road', 'city': 'London', 'zip': 'TW1 1DZ', 'lat': 51.4556, 'lng': -0.3334},
    {'name': 'Kingston Market Square', 'type': 'commercial', 'street': '56 Market Place', 'city': 'London', 'zip': 'KT1 1JT', 'lat': 51.4112, 'lng': -0.3045},
    {'name': 'Wimbledon Village House', 'type': 'house', 'street': '78 High Street', 'city': 'London', 'zip': 'SW19 5EE', 'lat': 51.4223, 'lng': -0.2056},
    {'name': 'Putney Bridge Apartments', 'type': 'flat', 'street': '90 Upper Richmond Road', 'city': 'London', 'zip': 'SW15 2SU', 'lat': 51.4634, 'lng': -0.2156},
]

print(f"\n🏢 Creating 50 properties across London...")
property_ids = []
for i, prop_data in enumerate(properties_data, 1):
    try:
        property_id = models.execute_kw(db, uid, password,
            'property_fielder.property', 'create',
            [{
                'name': prop_data['name'],
                'property_type': prop_data['type'],
                'street': prop_data['street'],
                'city': prop_data['city'],
                'zip': prop_data['zip'],
                'country_id': uk_id,
                'latitude': prop_data['lat'],
                'longitude': prop_data['lng'],
            }]
        )
        property_ids.append(property_id)
        print(f"   ✅ [{i}/50] Created: {prop_data['name']} (ID: {property_id})")
    except Exception as e:
        print(f"   ❌ [{i}/50] Failed to create {prop_data['name']}: {e}")

print(f"\n✅ Successfully created {len(property_ids)} properties")

# Verify the data
property_count = models.execute_kw(db, uid, password,
    'property_fielder.property', 'search_count',
    [[]]
)

inspector_count = models.execute_kw(db, uid, password,
    'res.partner', 'search_count',
    [[['name', 'in', ['Alice Johnson', 'Bob Smith', 'Carol Davis']]]]
)

# Get property type breakdown
property_types = {}
for prop_id in property_ids:
    prop = models.execute_kw(db, uid, password,
        'property_fielder.property', 'read',
        [[prop_id], ['property_type']]
    )[0]
    prop_type = prop['property_type']
    property_types[prop_type] = property_types.get(prop_type, 0) + 1

print(f"\n📊 Final Data Summary:")
print(f"   Total Properties: {property_count}")
print(f"   New Properties Created: {len(property_ids)}")
print(f"   Inspectors: {inspector_count}")
print(f"\n   Property Type Breakdown:")
for prop_type, count in sorted(property_types.items()):
    print(f"      - {prop_type}: {count}")

if len(property_ids) == 50 and inspector_count >= 3:
    print("\n🎉 SUCCESS! Full 50-property demo dataset loaded!")
    print("   ✅ 50 properties across London")
    print("   ✅ 3 inspectors (Alice, Bob, Carol)")
    print("   ✅ Multi-day test scenario ready")
else:
    print(f"\n⚠️  Warning: Expected 50 properties and 3 inspectors")
    print(f"   Got {len(property_ids)} new properties and {inspector_count} inspectors")

