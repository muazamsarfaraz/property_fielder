# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder - Owner Portal',
    'version': '18.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Self-service portal for property owners/landlords',
    'description': """
Property Fielder Owner Portal
=============================

Self-service portal for landlords/property owners to:
- View their property portfolio
- Check compliance status (FLAGE+ certifications)
- Download certificates and documents
- View upcoming inspections
- Request schedule changes

UK-specific features:
- FLAGE+ compliance visibility
- Certificate downloads
- Inspection scheduling
    """,
    'author': 'Property Fielder',
    'website': 'https://propertyfielder.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'portal',
        'website',
        'property_fielder_property_management',
        'property_fielder_field_service',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_security.xml',
        'views/portal_templates.xml',
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'property_fielder_owner_portal/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}

