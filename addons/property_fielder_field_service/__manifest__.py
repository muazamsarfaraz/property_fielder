# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder Field Service',
    'version': '1.0.0',
    'category': 'Fielder',
    'summary': 'AI-Powered Job Dispatch and Route Optimization',
    'description': """
Property Fielder Field Service Management
===================================

Complete field service management solution with AI-powered route optimization.

Key Features:
-------------
* Job/Visit Management - Schedule and track customer visits
* Inspector/Technician Management - Manage your mobile workforce
* Route Optimization - AI-powered routing with Timefold Solver
* Skills-Based Assignment - Match jobs to qualified technicians
* Time Window Constraints - Respect customer availability
* Multi-Day Planning - Plan routes across multiple days
* Real-Time Visualization - Interactive maps and timelines
* Mobile-Friendly - Access from any device

Perfect For:
------------
* Property Inspection Companies
* HVAC, Plumbing, Electrical Services
* Home Health Care
* Equipment Maintenance
* Mobile Service Providers

Technical:
----------
* Integrates with Timefold Solver for optimization
* Optional OSRM integration for real road routing
* Fallback to Haversine distance calculation
* RESTful API for external integrations
    """,
    'author': 'Fielder',
    'website': 'https://fielder.one',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'contacts',
        'hr',  # For employee/inspector management
        'project',  # For job/task management
    ],
    'data': [
        # Security
        'security/field_service_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence_data.xml',
        'data/skill_data.xml',
        'data/email_templates.xml',

        # Views (load actions first, then menus)
        'views/job_views.xml',
        'views/inspector_views.xml',
        'views/route_views.xml',
        'views/skill_views.xml',
        'views/optimization_views.xml',
        'views/change_request_views.xml',
        'views/dashboard.xml',
        'views/dispatch_view.xml',
        'views/menu.xml',  # Load menu last after all actions are defined

        # Wizards
        'wizard/share_schedule_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # External Libraries
            ('include', 'web._assets_helpers'),

            # Mapbox GL JS
            'https://api.mapbox.com/mapbox-gl-js/v3.0.1/mapbox-gl.css',
            'https://api.mapbox.com/mapbox-gl-js/v3.0.1/mapbox-gl.js',

            # Vis-Timeline
            'https://unpkg.com/vis-timeline@7.7.3/styles/vis-timeline-graph2d.min.css',
            'https://unpkg.com/vis-timeline@7.7.3/standalone/umd/vis-timeline-graph2d.min.js',

            # CSS
            'property_fielder_field_service/static/src/css/dispatch_view.css',
            'property_fielder_field_service/static/src/css/enhanced_dispatch.css',

            # JavaScript - Core Components
            'property_fielder_field_service/static/src/js/floating_panel.js',
            'property_fielder_field_service/static/src/js/dispatch_map_widget.js',
            'property_fielder_field_service/static/src/js/dispatch_timeline_widget.js',
            'property_fielder_field_service/static/src/js/dispatch_view.js',
            'property_fielder_field_service/static/src/js/enhanced_dispatch_view.js',

            # XML Templates
            'property_fielder_field_service/static/src/xml/floating_panel.xml',
            'property_fielder_field_service/static/src/xml/dispatch_map_widget.xml',
            'property_fielder_field_service/static/src/xml/dispatch_timeline_widget.xml',
            'property_fielder_field_service/static/src/xml/dispatch_view.xml',
            'property_fielder_field_service/static/src/xml/enhanced_dispatch_view.xml',
        ],
    },
    'demo': [
        # Demo Data: 50 Properties, 3 Inspectors (Multi-Day Test Scenario)
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 299.00,
    'currency': 'USD',
}

