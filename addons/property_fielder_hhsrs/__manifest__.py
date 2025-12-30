# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder HHSRS',
    'version': '17.0.1.0.0',
    'category': 'Property Management/Compliance',
    'summary': 'HHSRS, Decent Homes Standard & Awaab\'s Law Compliance',
    'description': """
Property Fielder HHSRS Module
=============================

Housing Health and Safety Rating System (HHSRS), Decent Homes Standard, 
and Awaab's Law compliance for UK social housing.

Features:
---------
* Full 29 HHSRS hazard categories with scoring
* 16 official likelihood bands with RSP values
* HHSRS score calculation (Likelihood × Outcome)
* Band assignment (A-J) and Category 1/2 classification
* Awaab's Law deadline tracking (24hr emergency, 7/14 day non-emergency)
* Damp & Mould tracking with timeline
* Decent Homes Standard 4-criteria assessment
* Building component condition tracking
* Automated deadline alerts and breach notifications

Legal Compliance:
-----------------
* Housing Act 2004 (HHSRS)
* Awaab's Law (Social Housing Regulation Act 2023)
* Decent Homes Standard
    """,
    'author': 'Property Fielder',
    'website': 'https://propertyfielder.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
        'property_fielder_property_management',
    ],
    'data': [
        # Security
        'security/hhsrs_security.xml',
        'security/ir.model.access.csv',
        
        # Data (reference data must load first)
        'data/sequence_data.xml',
        'data/hazard_type_data.xml',
        'data/likelihood_band_data.xml',
        'data/vulnerable_group_data.xml',
        'data/ir_config_parameter.xml',
        'data/cron_data.xml',
        
        # Views
        'views/hazard_type_views.xml',
        'views/likelihood_band_views.xml',
        'views/vulnerable_group_views.xml',
        'views/hhsrs_assessment_views.xml',
        'views/awaab_deadline_views.xml',
        'views/damp_mould_views.xml',
        'views/dhs_assessment_views.xml',
        'views/building_component_views.xml',
        'views/menu_views.xml',
        
        # Reports
        'reports/hhsrs_assessment_report.xml',
        'reports/dhs_assessment_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

