# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re


class SMSTemplate(models.Model):
    """SMS Templates for different notification types"""
    
    _name = 'property_fielder.sms.template'
    _description = 'SMS Template'
    _order = 'name'
    
    name = fields.Char(string='Template Name', required=True)
    code = fields.Char(string='Template Code', required=True,
                       help='Unique code to identify template, e.g., appointment_confirmation')
    active = fields.Boolean(string='Active', default=True)
    
    message_body = fields.Text(string='Message Body', required=True,
                               help='Use {variable_name} for dynamic content')
    
    # Template type
    template_type = fields.Selection([
        ('confirmation', 'Appointment Confirmation'),
        ('reminder', 'Appointment Reminder'),
        ('reschedule', 'Reschedule Notification'),
        ('completion', 'Inspection Complete'),
        ('cancelled', 'Appointment Cancelled'),
        ('custom', 'Custom'),
    ], string='Template Type', default='custom')
    
    # Available variables help text
    available_variables = fields.Text(
        string='Available Variables',
        compute='_compute_available_variables',
        store=False
    )
    
    @api.depends('template_type')
    def _compute_available_variables(self):
        """Show available variables based on template type"""
        job_vars = """
Available variables for Job templates:
- {owner_name} - Property owner name
- {property_address} - Full property address
- {scheduled_date} - Scheduled date
- {scheduled_time} - Scheduled time window
- {inspector_name} - Inspector name
- {job_type} - Type of inspection
- {confirmation_link} - Link to confirm/reschedule
- {company_name} - Your company name
- {company_phone} - Your company phone
"""
        for rec in self:
            rec.available_variables = job_vars
    
    def render_message(self, values):
        """Render template with provided values"""
        self.ensure_one()
        message = self.message_body
        for key, value in values.items():
            placeholder = '{%s}' % key
            message = message.replace(placeholder, str(value or ''))
        # Remove any unreplaced placeholders
        message = re.sub(r'\{[^}]+\}', '', message)
        return message.strip()
    
    @api.model
    def get_template(self, code):
        """Get template by code"""
        template = self.search([('code', '=', code), ('active', '=', True)], limit=1)
        return template

