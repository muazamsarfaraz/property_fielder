# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder Field Service Mobile',
    'version': '1.0.1',  # Fixed model references in cron data
    'category': 'Fielder',
    'summary': 'Mobile app for field inspectors',
    'description': """
Property Fielder Field Service Mobile
===============================

Mobile application for field inspectors to:
- View assigned jobs and routes
- Navigate to job locations
- Check in/out of jobs
- Capture photos and signatures
- Add notes and complete jobs
- Work offline with sync

This addon provides a mobile-optimized interface and REST API for native mobile apps.
    """,
    'author': 'Fielder',
    'website': 'https://fielder.one',
    'license': 'LGPL-3',
    
    # Dependencies
    'depends': [
        'base',
        'web',
        # 'web_mobile',  # Removed - deprecated in Odoo 19
        'property_fielder_field_service',  # Main Field Service addon
    ],
    
    # Data files
    'data': [
        # Security
        'security/mobile_security.xml',
        'security/ir.model.access.csv',

        # Actions (must be loaded first)
        'views/mobile_actions.xml',

        # Views
        'views/mobile_menu_views.xml',
        'views/mobile_job_views.xml',
        'views/mobile_route_views.xml',
        'views/mobile_dashboard_views.xml',
        'views/mobile_photo_views.xml',

        # Templates
        'views/mobile_templates.xml',

        # Data - Cron jobs and templates
        'data/safety_timer_cron.xml',
    ],
    
    # Assets - Commented out until static files are created
    # 'assets': {
    #     'web.assets_backend': [
    #         'property_fielder_field_service_mobile/static/src/css/mobile.css',
    #         'property_fielder_field_service_mobile/static/src/js/mobile_app.js',
    #         'property_fielder_field_service_mobile/static/src/js/geolocation.js',
    #         'property_fielder_field_service_mobile/static/src/js/camera.js',
    #         'property_fielder_field_service_mobile/static/src/js/offline_sync.js',
    #     ],
    #     'web.assets_frontend': [
    #         'property_fielder_field_service_mobile/static/src/css/mobile_frontend.css',
    #         'property_fielder_field_service_mobile/static/src/js/mobile_frontend.js',
    #     ],
    # },
    
    # Installation
    'installable': True,
    'application': False,  # This is a companion addon
    'auto_install': False,
    
    # Mobile-specific
    'mobile_compatible': True,
    
    # Images
    'images': ['static/description/icon.png'],
}

