# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder Templates',
    'version': '19.0.1.0.0',
    'category': 'Property Management/Inspections',
    'summary': 'Template-driven Inspections for Property Compliance',
    'description': """
Property Fielder Templates Module
=================================

Template-driven inspections for mobile app - foundation for all inspection types.

Features:
---------
* Configurable inspection templates with sections and items
* Multiple response types (yes/no, pass/fail, numeric, text, photo, signature, etc.)
* Skip logic for conditional display of sections/items
* Template versioning (draft/active/archived)
* Automatic defect creation from failures
* Asset iteration for CP12/EICR inspections
* Previous value pre-fill for re-inspections
* Scoring and calculation engine

Default Templates:
------------------
* Quick Visit (minimal checks)
* Full HHSRS (29 hazard categories)
* Gas Safety (CP12 format with ID/AR/NCS codes)
* EICR (18th Edition with C1/C2/C3/FI codes)
* Fire Risk Assessment

Technical:
----------
* Matrix and tabular response types with JSON storage
* Conditional validation rules
* Inspector license snapshots for certifications
    """,
    'author': 'Property Fielder',
    'website': 'https://propertyfielder.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
        'property_fielder_property_management',
        'property_fielder_field_service',
    ],
    'data': [
        # Security
        'security/templates_security.xml',
        'security/ir.model.access.csv',
        
        # Data (reference data first)
        'data/sequence_data.xml',
        'data/template_data.xml',
        
        # Views
        'views/inspection_template_views.xml',
        'views/template_section_views.xml',
        'views/template_item_views.xml',
        'views/inspection_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

