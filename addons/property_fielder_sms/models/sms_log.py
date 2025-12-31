# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SMSLog(models.Model):
    """Log of all SMS messages sent"""
    
    _name = 'property_fielder.sms.log'
    _description = 'SMS Log'
    _order = 'create_date desc'
    _rec_name = 'to_number'
    
    to_number = fields.Char(string='To Number', required=True, index=True)
    from_number = fields.Char(string='From Number')
    message_body = fields.Text(string='Message')
    
    # Status tracking
    status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('received', 'Received'),  # For incoming messages
    ], string='Status', default='pending', index=True)
    
    error_message = fields.Text(string='Error Message')
    
    # Twilio reference
    twilio_sid = fields.Char(string='Twilio Message SID', index=True)
    
    # Direction
    direction = fields.Selection([
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
    ], string='Direction', default='outbound')
    
    # Related records
    job_id = fields.Many2one('property_fielder.job', string='Related Job', index=True)
    partner_id = fields.Many2one('res.partner', string='Related Contact', index=True)
    template_id = fields.Many2one('property_fielder.sms.template', string='Template Used')
    
    # Timing
    sent_time = fields.Datetime(string='Sent Time')
    delivered_time = fields.Datetime(string='Delivered Time')
    
    # Message type
    message_type = fields.Selection([
        ('confirmation', 'Confirmation'),
        ('reminder', 'Reminder'),
        ('reschedule', 'Reschedule'),
        ('completion', 'Completion'),
        ('reply', 'Reply'),
        ('custom', 'Custom'),
    ], string='Message Type', default='custom')
    
    # Cost tracking (Twilio charges per segment)
    segment_count = fields.Integer(string='Segments', default=1)
    
    def name_get(self):
        """Custom display name"""
        result = []
        for rec in self:
            name = f"{rec.to_number} - {rec.status} ({rec.create_date.strftime('%Y-%m-%d %H:%M') if rec.create_date else 'N/A'})"
            result.append((rec.id, name))
        return result

