# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccessAttempt(models.Model):
    """Log of access attempts for defect remediation."""
    
    _name = 'property_fielder.access.attempt'
    _description = 'Access Attempt'
    _order = 'attempt_date desc'
    
    defect_id = fields.Many2one(
        'property_fielder.defect',
        string='Defect',
        required=True,
        ondelete='cascade'
    )
    
    property_id = fields.Many2one(
        related='defect_id.property_id',
        store=True,
        string='Property'
    )
    
    attempt_date = fields.Datetime(
        string='Attempt Date',
        required=True,
        default=fields.Datetime.now
    )
    
    result = fields.Selection([
        ('granted', 'Access Granted'),
        ('refused', 'Access Refused'),
        ('no_answer', 'No Answer'),
        ('rescheduled', 'Rescheduled'),
    ], string='Result', required=True)
    
    reason = fields.Text(
        string='Reason',
        help='Reason for refusal or reschedule'
    )
    
    contractor_id = fields.Many2one(
        'res.partner',
        string='Contractor',
        domain=[('is_company', '=', True)],
        help='Contractor who attempted access'
    )
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        help='Inspector who attempted access'
    )
    
    notes = fields.Text(string='Notes')
    
    # Evidence photos
    photo_ids = fields.Many2many(
        'ir.attachment',
        'access_attempt_photo_rel',
        'attempt_id',
        'attachment_id',
        string='Evidence Photos',
        help='Photos taken as evidence (e.g., door photo)'
    )
    
    # Rescheduled date if applicable
    rescheduled_date = fields.Datetime(
        string='Rescheduled To',
        help='New date if access was rescheduled'
    )
    
    def name_get(self):
        result = []
        for record in self:
            date_str = record.attempt_date.strftime('%Y-%m-%d %H:%M') if record.attempt_date else ''
            name = f"{record.defect_id.name} - {date_str} ({record.result})"
            result.append((record.id, name))
        return result

