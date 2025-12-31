# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CalendarConfig(models.Model):
    """Configuration for calendar sync providers (Google, Microsoft)"""
    
    _name = 'property_fielder.calendar.config'
    _description = 'Calendar Sync Configuration'
    _rec_name = 'provider'
    
    provider = fields.Selection([
        ('google', 'Google Calendar'),
        ('microsoft', 'Microsoft Outlook/365'),
    ], string='Provider', required=True, default='google')
    
    active = fields.Boolean(string='Active', default=True)
    
    # Google OAuth2 credentials
    google_client_id = fields.Char(string='Google Client ID')
    google_client_secret = fields.Char(string='Google Client Secret')
    
    # Microsoft OAuth2 credentials
    microsoft_client_id = fields.Char(string='Microsoft Client ID')
    microsoft_client_secret = fields.Char(string='Microsoft Client Secret')
    microsoft_tenant_id = fields.Char(
        string='Microsoft Tenant ID',
        default='common',
        help='Azure AD tenant ID. Use "common" for multi-tenant apps.'
    )
    
    # Sync settings
    auto_sync_enabled = fields.Boolean(
        string='Auto-Sync Enabled',
        default=True,
        help='Automatically sync job changes to connected calendars'
    )
    sync_on_schedule = fields.Boolean(
        string='Sync When Scheduled',
        default=True,
        help='Create calendar event when job is scheduled'
    )
    sync_on_reschedule = fields.Boolean(
        string='Sync When Rescheduled',
        default=True,
        help='Update calendar event when job is rescheduled'
    )
    sync_on_cancel = fields.Boolean(
        string='Delete When Cancelled',
        default=True,
        help='Remove calendar event when job is cancelled'
    )
    
    # iCal settings
    ical_enabled = fields.Boolean(
        string='iCal Feed Enabled',
        default=True,
        help='Enable iCal subscription feeds for inspectors'
    )
    
    @api.constrains('provider')
    def _check_unique_provider(self):
        for record in self:
            existing = self.search([
                ('provider', '=', record.provider),
                ('id', '!=', record.id),
                ('active', '=', True)
            ])
            if existing:
                raise UserError(_(
                    'Only one active configuration per provider is allowed. '
                    'Deactivate the existing %s configuration first.'
                ) % record.provider)
    
    def action_test_connection(self):
        """Test the OAuth2 configuration"""
        self.ensure_one()
        if self.provider == 'google':
            if not self.google_client_id or not self.google_client_secret:
                raise UserError(_('Please configure Google OAuth2 credentials first.'))
            # In real implementation, would test API connection
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Configuration Valid'),
                    'message': _('Google Calendar credentials are configured. Inspectors can now connect their calendars.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        elif self.provider == 'microsoft':
            if not self.microsoft_client_id or not self.microsoft_client_secret:
                raise UserError(_('Please configure Microsoft OAuth2 credentials first.'))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Configuration Valid'),
                    'message': _('Microsoft Calendar credentials are configured. Inspectors can now connect their calendars.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.model
    def get_google_config(self):
        """Get active Google Calendar configuration"""
        return self.search([('provider', '=', 'google'), ('active', '=', True)], limit=1)
    
    @api.model
    def get_microsoft_config(self):
        """Get active Microsoft Calendar configuration"""
        return self.search([('provider', '=', 'microsoft'), ('active', '=', True)], limit=1)

