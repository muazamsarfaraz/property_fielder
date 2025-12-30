# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json


class MobileSyncLog(models.Model):
    """Track mobile app sync operations"""
    
    _name = 'property_fielder.mobile.sync'
    _description = 'Mobile Sync Log'
    _order = 'sync_time desc'
    
    # Inspector
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        help='Inspector who synced'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        help='User account'
    )
    
    # Sync Details
    sync_time = fields.Datetime(
        string='Sync Time',
        required=True,
        default=fields.Datetime.now,
        help='When sync occurred'
    )
    
    sync_type = fields.Selection([
        ('full', 'Full Sync'),
        ('incremental', 'Incremental Sync'),
        ('upload', 'Upload Only'),
        ('download', 'Download Only')
    ], string='Sync Type', default='incremental', required=True)
    
    # Statistics
    jobs_downloaded = fields.Integer(
        string='Jobs Downloaded',
        default=0,
        help='Number of jobs downloaded'
    )
    
    jobs_uploaded = fields.Integer(
        string='Jobs Uploaded',
        default=0,
        help='Number of jobs uploaded'
    )
    
    photos_uploaded = fields.Integer(
        string='Photos Uploaded',
        default=0,
        help='Number of photos uploaded'
    )
    
    signatures_uploaded = fields.Integer(
        string='Signatures Uploaded',
        default=0,
        help='Number of signatures uploaded'
    )
    
    notes_uploaded = fields.Integer(
        string='Notes Uploaded',
        default=0,
        help='Number of notes uploaded'
    )
    
    checkins_uploaded = fields.Integer(
        string='Check-Ins Uploaded',
        default=0,
        help='Number of check-ins uploaded'
    )
    
    # Status
    status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed')
    ], string='Status', default='success', required=True)
    
    error_message = fields.Text(
        string='Error Message',
        help='Error details if sync failed'
    )
    
    # Device Info
    device_id = fields.Char(
        string='Device ID',
        help='Unique device identifier'
    )
    
    device_info = fields.Char(
        string='Device Info',
        help='Device model and OS version'
    )
    
    app_version = fields.Char(
        string='App Version',
        help='Mobile app version'
    )
    
    # Network
    network_type = fields.Char(
        string='Network Type',
        help='Network type (WiFi, 4G, etc.)'
    )
    
    # Duration
    duration_seconds = fields.Float(
        string='Duration (seconds)',
        help='How long sync took'
    )
    
    # Data Size
    data_size_kb = fields.Float(
        string='Data Size (KB)',
        help='Amount of data transferred'
    )


class MobileDevice(models.Model):
    """Registered mobile devices"""
    
    _name = 'property_fielder.mobile.device'
    _description = 'Mobile Device'
    
    # Device Info
    device_id = fields.Char(
        string='Device ID',
        required=True,
        help='Unique device identifier'
    )
    
    device_name = fields.Char(
        string='Device Name',
        help='User-friendly device name'
    )
    
    device_model = fields.Char(
        string='Device Model',
        help='Device model (e.g., iPhone 14, Samsung Galaxy S23)'
    )
    
    os_version = fields.Char(
        string='OS Version',
        help='Operating system version'
    )
    
    # Inspector
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        help='Inspector using this device'
    )
    
    # Registration
    registered_date = fields.Datetime(
        string='Registered Date',
        default=fields.Datetime.now,
        help='When device was registered'
    )
    
    last_sync = fields.Datetime(
        string='Last Sync',
        help='Last successful sync time'
    )
    
    # Status
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help='Is device active'
    )
    
    # Push Notifications
    push_token = fields.Char(
        string='Push Token',
        help='Token for push notifications'
    )

    # Constraints (Odoo 19 style)
    _check_device_id_unique = models.Constraint(
        'UNIQUE(device_id)',
        'Device ID must be unique!',
    )

