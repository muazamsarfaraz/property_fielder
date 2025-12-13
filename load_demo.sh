#!/bin/bash
# Load demo data for Property Fielder Field Service addon

docker exec property_fielder_odoo python3 << 'PYTHON_SCRIPT'
import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import convert

# Initialize Odoo environment
odoo.tools.config.parse_config(['-d', 'property_fielder', '--no-http'])
with api.Environment.manage():
    registry = odoo.registry('property_fielder')
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Load the demo data XML file
        demo_file = '/mnt/extra-addons/property_fielder_field_service/data/demo_data.xml'
        
        print(f"📦 Loading demo data from: {demo_file}")
        
        try:
            convert.convert_file(
                cr,
                'property_fielder_field_service',
                demo_file,
                None,
                mode='init',
                noupdate=True,
                kind='demo'
            )
            cr.commit()
            
            print("✅ Demo data loaded successfully!")
            
            # Verify the data
            Property = env['property_fielder.property']
            Partner = env['res.partner']
            
            property_count = Property.search_count([])
            inspector_count = Partner.search_count([
                ('name', 'in', ['Alice Johnson', 'Bob Smith', 'Carol Davis'])
            ])
            
            print(f"\n📊 Data Summary:")
            print(f"   Properties: {property_count}")
            print(f"   Inspectors: {inspector_count}")
            
            if property_count == 50 and inspector_count == 3:
                print("\n🎉 SUCCESS! All 50 properties and 3 inspectors loaded!")
            else:
                print(f"\n⚠️  Expected 50 properties and 3 inspectors")
                print(f"   Got {property_count} properties and {inspector_count} inspectors")
                
        except Exception as e:
            print(f"❌ Error loading demo data: {e}")
            import traceback
            traceback.print_exc()
            cr.rollback()

PYTHON_SCRIPT

