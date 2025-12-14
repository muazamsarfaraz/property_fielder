#!/usr/bin/env python3
"""Update Odoo modules via XML-RPC"""
import xmlrpc.client
import sys

url = 'https://propertyfielder-production.up.railway.app'
db = 'railway'
username = 'admin'
password = sys.argv[1] if len(sys.argv) > 1 else 'admin'

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f'Authenticated as uid: {uid}')

if uid:
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Update module list first
    print('Updating module list...')
    models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
    
    # Find our modules and trigger upgrade
    modules = [
        'property_fielder_field_service',
        'property_fielder_field_service_mobile', 
        'property_fielder_property_management'
    ]
    
    for mod_name in modules:
        mod_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[['name', '=', mod_name]]])
        if mod_ids:
            mod = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [mod_ids, ['name', 'state', 'category_id', 'author']])
            state = mod[0]['state']
            category = mod[0]['category_id']
            author = mod[0]['author']
            print(f'{mod_name}: state={state}, category={category}, author={author}')
            
            if state == 'installed':
                print(f'  Upgrading {mod_name}...')
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [mod_ids])
                print(f'  Done!')
            elif state == 'uninstalled':
                print(f'  Installing {mod_name}...')
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [mod_ids])
                print(f'  Done!')
        else:
            print(f'{mod_name}: NOT FOUND in database')
    
    print('\nAll modules processed!')
else:
    print('Authentication failed - check password')

