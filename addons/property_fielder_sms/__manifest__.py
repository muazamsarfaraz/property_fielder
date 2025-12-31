# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder - SMS Integration',
    'version': '18.0.1.0.0',
    'category': 'Services/Field Service',
    'summary': 'Twilio SMS integration for appointment notifications',
    'description': """
        SMS Integration for Property Fielder
        ====================================
        
        Features:
        - Twilio SMS integration for sending notifications
        - Appointment confirmation SMS
        - Reminder SMS before inspections
        - Status update notifications
        - Two-way SMS for confirmations/reschedules
        - SMS templates with variable substitution
        - SMS log for tracking all messages
    """,
    'author': 'MCB Platform',
    'depends': [
        'base',
        'mail',
        'property_fielder_field_service',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sms_templates.xml',
        'views/sms_config_views.xml',
        'views/sms_log_views.xml',
        'views/job_sms_views.xml',
        'views/menu_views.xml',
    ],
    'external_dependencies': {
        'python': ['twilio'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

