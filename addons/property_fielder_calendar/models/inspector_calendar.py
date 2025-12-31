# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid
import logging

_logger = logging.getLogger(__name__)


class InspectorCalendar(models.Model):
    """Links an inspector to their external calendar account"""
    
    _name = 'property_fielder.inspector.calendar'
    _description = 'Inspector Calendar Connection'
    _rec_name = 'inspector_id'
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        ondelete='cascade'
    )
    
    provider = fields.Selection([
        ('google', 'Google Calendar'),
        ('microsoft', 'Microsoft Outlook/365'),
    ], string='Provider', required=True)
    
    # OAuth2 tokens (encrypted in production)
    access_token = fields.Char(string='Access Token')
    refresh_token = fields.Char(string='Refresh Token')
    token_expiry = fields.Datetime(string='Token Expiry')
    
    # Calendar selection
    calendar_id = fields.Char(
        string='Calendar ID',
        help='External calendar ID to sync with'
    )
    calendar_name = fields.Char(string='Calendar Name')
    
    # iCal feed token
    ical_token = fields.Char(
        string='iCal Token',
        default=lambda self: str(uuid.uuid4()),
        help='Secret token for iCal feed URL'
    )
    
    # Status
    connection_status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('error', 'Error'),
    ], string='Status', default='disconnected')
    
    last_sync = fields.Datetime(string='Last Sync')
    last_error = fields.Text(string='Last Error')
    
    sync_enabled = fields.Boolean(
        string='Sync Enabled',
        default=True,
        help='Enable automatic sync for this inspector'
    )
    
    # Stats
    events_synced = fields.Integer(
        string='Events Synced',
        compute='_compute_events_synced'
    )
    
    _sql_constraints = [
        ('inspector_provider_unique', 
         'UNIQUE(inspector_id, provider)',
         'Inspector can only have one connection per provider!')
    ]
    
    @api.depends('inspector_id')
    def _compute_events_synced(self):
        CalendarEvent = self.env['property_fielder.job.calendar.event']
        for record in self:
            record.events_synced = CalendarEvent.search_count([
                ('inspector_calendar_id', '=', record.id)
            ])
    
    def action_connect(self):
        """Initiate OAuth2 connection flow"""
        self.ensure_one()
        config = self._get_provider_config()
        if not config:
            raise UserError(_(
                'No %s configuration found. Please configure OAuth2 credentials first.'
            ) % self.provider)
        
        # Generate OAuth2 authorization URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirect_uri = f"{base_url}/calendar/oauth/{self.provider}/callback"
        
        if self.provider == 'google':
            auth_url = self._get_google_auth_url(config, redirect_uri)
        else:
            auth_url = self._get_microsoft_auth_url(config, redirect_uri)
        
        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'new',
        }
    
    def _get_provider_config(self):
        """Get the provider configuration"""
        Config = self.env['property_fielder.calendar.config']
        if self.provider == 'google':
            return Config.get_google_config()
        return Config.get_microsoft_config()
    
    def _get_google_auth_url(self, config, redirect_uri):
        """Generate Google OAuth2 authorization URL"""
        from urllib.parse import urlencode
        params = {
            'client_id': config.google_client_id,
            'redirect_uri': redirect_uri,
            'scope': 'https://www.googleapis.com/auth/calendar',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': str(self.id),
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    def _get_microsoft_auth_url(self, config, redirect_uri):
        """Generate Microsoft OAuth2 authorization URL"""
        from urllib.parse import urlencode
        tenant = config.microsoft_tenant_id or 'common'
        params = {
            'client_id': config.microsoft_client_id,
            'redirect_uri': redirect_uri,
            'scope': 'Calendars.ReadWrite offline_access',
            'response_type': 'code',
            'state': str(self.id),
        }
        return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?{urlencode(params)}"
    
    def action_disconnect(self):
        """Disconnect the calendar"""
        self.ensure_one()
        self.write({
            'access_token': False,
            'refresh_token': False,
            'token_expiry': False,
            'connection_status': 'disconnected',
            'calendar_id': False,
            'calendar_name': False,
        })
    
    def action_regenerate_ical_token(self):
        """Generate new iCal token (invalidates old feeds)"""
        self.ensure_one()
        self.ical_token = str(uuid.uuid4())
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Token Regenerated'),
                'message': _('New iCal token generated. Old feed URLs will no longer work.'),
                'type': 'warning',
                'sticky': False,
            }
        }

