# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder - Defects & Faults',
    'version': '19.0.1.0.0',
    'category': 'Property Management',
    'summary': 'Unified defect/fault tracking with industry codes and SLA management',
    'description': """
Property Fielder Defects & Faults
=================================

Unified defect tracking from discovery through remediation with:
- Industry fault codes (GIUSP, 18th Edition, RRO 2005, HSE L8, CAR 2012)
- Cat 1/Cat 2 severity classification
- SLA deadline calculation and breach tracking
- Contractor assignment and cost approval workflow
- Integration with inspection templates
- Before/after photo evidence
- Section 21 blocking for outstanding hazards

Fault Code Categories:
- Gas: ID (Immediately Dangerous), AR (At Risk), NCS (Not to Current Standard)
- Electrical: C1 (Danger Present), C2 (Potentially Dangerous), C3 (Improvement Recommended)
- Fire: FSH (Fire Safety Hazard), FSR (Fire Safety Risk), FSI (Fire Safety Improvement)
- Legionella: LAC (Legionella Action Critical), LRF (Legionella Risk Found), LMI (Legionella Minor Issue)
- Asbestos: ADF (Asbestos Danger Found), ARD (Asbestos Removal Due), AIM (Asbestos In-situ Management)
    """,
    'author': 'Property Fielder',
    'website': 'https://propertyfielder.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'property_fielder_property_management',
        'property_fielder_templates',
        'property_fielder_hhsrs',
    ],
    'data': [
        # Security
        'security/defects_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/ir_sequence_data.xml',
        'data/fault_code_data.xml',
        # Views
        'views/fault_code_views.xml',
        'views/defect_views.xml',
        'views/defect_photo_views.xml',
        'views/access_attempt_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

