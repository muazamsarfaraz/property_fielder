#!/usr/bin/env python3
"""Create inspector user via XML-RPC"""
import xmlrpc.client

url = 'https://propertyfielder-production.up.railway.app'
db = 'railway'
username = 'admin'
password = 'admin'

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f'Authenticated as uid: {uid}')

if uid:
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Check existing users
    users = models.execute_kw(db, uid, password, 'res.users', 'search_read', 
        [[]], {'fields': ['login', 'name'], 'limit': 20})
    print('Existing users:')
    for u in users:
        print(f"  - {u['login']}: {u['name']}")
    
    # Check if inspector user exists
    inspector_exists = models.execute_kw(db, uid, password, 'res.users', 'search', 
        [[['login', '=', 'inspector']]])
    
    if not inspector_exists:
        print('\nCreating inspector user...')
        user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [{
            'name': 'Test Inspector',
            'login': 'inspector',
            'password': 'inspector123',
        }])
        print(f'Created user with ID: {user_id}')
        
        # Now create an inspector profile linked to this user
        print('Creating inspector profile...')
        inspector_id = models.execute_kw(db, uid, password, 'property_fielder.inspector', 'create', [{
            'name': 'Test Inspector',
            'user_id': user_id,
            'home_latitude': 51.5074,
            'home_longitude': -0.1278,
            'shift_start': 8.0,
            'shift_end': 18.0,
            'vehicle_capacity': 8,
            'active': True,
        }])
        print(f'Created inspector profile with ID: {inspector_id}')
    else:
        print(f'\nInspector user already exists with ID: {inspector_exists[0]}')
        
        # Check if inspector profile exists
        inspector_profile = models.execute_kw(db, uid, password, 'property_fielder.inspector', 'search', 
            [[['user_id', '=', inspector_exists[0]]]])
        if inspector_profile:
            print(f'Inspector profile exists with ID: {inspector_profile[0]}')
        else:
            print('No inspector profile found, creating one...')
            inspector_id = models.execute_kw(db, uid, password, 'property_fielder.inspector', 'create', [{
                'name': 'Test Inspector',
                'user_id': inspector_exists[0],
                'home_latitude': 51.5074,
                'home_longitude': -0.1278,
                'shift_start': 8.0,
                'shift_end': 18.0,
                'vehicle_capacity': 8,
                'active': True,
            }])
            print(f'Created inspector profile with ID: {inspector_id}')
else:
    print('Authentication failed!')

