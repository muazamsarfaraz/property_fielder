# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder Analytics',
    'version': '17.0.1.0.0',
    'category': 'Field Service/Analytics',
    'summary': 'Analytics and reporting for field service operations',
    'description': '''
Property Fielder Analytics
==========================

Comprehensive analytics and reporting for field service operations:

Features:
---------
* Inspector Productivity Reports
  - Jobs completed per inspector
  - Average job duration
  - On-time completion rate
  - Travel time analysis
  
* Compliance Trend Analytics
  - Compliance rate over time
  - Expiry forecasts
  - Risk analysis
  
* Cost Analysis
  - Cost per inspection
  - Route efficiency metrics
  - Budget vs actual

* Dashboard with KPIs
* Export to Excel/PDF
    ''',
    'author': 'Property Fielder',
    'website': 'https://www.propertyfielder.com',
    'license': 'LGPL-3',
    'depends': [
        'property_fielder_field_service',
        'property_fielder_property_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/inspector_productivity_views.xml',
        'views/compliance_analytics_views.xml',
        'views/cost_analysis_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

