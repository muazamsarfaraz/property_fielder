# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder Property Management',
    'version': '1.0.0',
    'category': 'Fielder',
    'summary': 'Property Management with FLAGE+ Certification Compliance',
    'description': """
Property Fielder Property Management
==============================

Comprehensive property management system with UK FLAGE+ certification compliance tracking.

FLAGE+ Certifications:
* F - Fire Safety
* L - Legionella Control
* A - Asbestos Management
* G - Gas Safety
* E - Electrical Safety

Features:
* Property portfolio management
* FLAGE+ certification tracking
* Configurable inspection schedules
* Compliance monitoring and alerts
* Expiry notifications
* Integration with field service for inspections
* Compliance reports and dashboards
* Multi-property support
* Tenant management
* Document storage for certificates
    """,
    'author': 'Fielder',
    'website': 'https://fielder.one',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
        'property_fielder_field_service',  # Integration with field service
    ],
    'data': [
        # Security
        'security/property_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/certification_type_data.xml',
        'data/compliance_requirement_data.xml',
        'data/sequence_data.xml',

        # Wizards
        'wizard/certification_type_wizard_views.xml',
        'wizard/create_jobs_wizard_views.xml',

        # Actions (must be loaded first)
        'views/actions.xml',

        # Views (order matters - actions must be defined before they are referenced)
        'views/certification_views.xml',
        'views/inspection_views.xml',
        'views/property_views.xml',
        'views/compliance_dashboard_views.xml',
        'views/menu_views.xml',

        # Reports
        'reports/compliance_report.xml',
        'reports/certificate_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

