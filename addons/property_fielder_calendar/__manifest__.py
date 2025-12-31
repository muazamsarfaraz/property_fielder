# -*- coding: utf-8 -*-
{
    'name': 'Property Fielder Calendar Sync',
    'version': '17.0.1.0.0',
    'category': 'Field Service/Calendar',
    'summary': 'Google & Outlook Calendar sync for jobs and inspections',
    'description': '''
Property Fielder Calendar Sync
==============================

Synchronize jobs and inspections with external calendars:

Features:
---------
* Google Calendar integration
* Microsoft Outlook/365 Calendar integration  
* Automatic event creation when jobs are scheduled
* Event updates when jobs are rescheduled
* Event deletion when jobs are cancelled
* iCal feed for read-only calendar subscriptions
* Inspector-specific calendar sync
* OAuth2 authentication for secure access

Configuration:
--------------
1. Set up Google Cloud credentials (Client ID, Client Secret)
2. Set up Microsoft Azure app credentials
3. Connect inspector calendars via OAuth flow
4. Enable auto-sync in settings
    ''',
    'author': 'Property Fielder',
    'website': 'https://www.propertyfielder.com',
    'license': 'LGPL-3',
    'depends': [
        'property_fielder_field_service',
        'calendar',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/calendar_config_views.xml',
        'views/inspector_calendar_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

