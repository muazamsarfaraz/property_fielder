# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SMSConfig(models.Model):
    """SMS Configuration - stores Twilio credentials and settings"""
    
    _name = 'property_fielder.sms.config'
    _description = 'SMS Configuration'
    _rec_name = 'name'
    
    name = fields.Char(string='Configuration Name', default='Twilio SMS', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Twilio Credentials
    account_sid = fields.Char(string='Account SID', required=True)
    auth_token = fields.Char(string='Auth Token', required=True)
    phone_number = fields.Char(string='Twilio Phone Number', required=True,
                               help='Phone number in E.164 format, e.g., +447888865100')
    
    # Settings
    use_test_credentials = fields.Boolean(string='Use Test Credentials', default=False,
                                          help='Use Twilio test credentials for development')
    test_account_sid = fields.Char(string='Test Account SID')
    test_auth_token = fields.Char(string='Test Auth Token')
    
    # Notification Settings
    send_confirmation_sms = fields.Boolean(string='Send Confirmation SMS', default=True)
    send_reminder_sms = fields.Boolean(string='Send Reminder SMS', default=True)
    reminder_hours_before = fields.Integer(string='Reminder Hours Before', default=24)
    send_completion_sms = fields.Boolean(string='Send Completion SMS', default=False)
    
    # Rate Limiting
    max_sms_per_day = fields.Integer(string='Max SMS per Day', default=1000)
    sms_sent_today = fields.Integer(string='SMS Sent Today', default=0, readonly=True)
    
    @api.model
    def get_config(self):
        """Get active SMS configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise UserError(_('No active SMS configuration found. Please configure SMS settings.'))
        return config
    
    def get_credentials(self):
        """Get Twilio credentials (test or production)"""
        self.ensure_one()
        if self.use_test_credentials:
            return {
                'account_sid': self.test_account_sid,
                'auth_token': self.test_auth_token,
                'phone_number': self.phone_number,
            }
        return {
            'account_sid': self.account_sid,
            'auth_token': self.auth_token,
            'phone_number': self.phone_number,
        }
    
    def action_test_sms(self):
        """Send a test SMS to verify configuration"""
        self.ensure_one()
        # This will be implemented by sms_service
        sms_service = self.env['property_fielder.sms.service']
        result = sms_service.send_sms(
            to_number='+447507121721',  # Test number
            message='Test SMS from Property Fielder. Configuration is working!',
            config=self
        )
        if result.get('success'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Test SMS sent successfully!'),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_('Failed to send test SMS: %s') % result.get('error'))
    
    @api.model
    def reset_daily_counter(self):
        """Cron job to reset daily SMS counter"""
        self.search([]).write({'sms_sent_today': 0})

