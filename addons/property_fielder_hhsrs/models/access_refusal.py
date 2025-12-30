# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AwaabAccessRefusal(models.Model):
    """Access refusal tracking - stops the clock on Awaab deadlines."""
    _name = 'property_fielder.awaab.access.refusal'
    _description = 'Awaab Access Refusal'
    _order = 'refusal_date desc'

    deadline_id = fields.Many2one(
        'property_fielder.awaab.deadline',
        string='Awaab Deadline',
        required=True,
        ondelete='cascade'
    )
    
    refusal_date = fields.Date(
        string='Refusal Date',
        required=True,
        default=fields.Date.today
    )
    
    reason = fields.Text(
        string='Reason',
        help='Reason given by tenant for refusing access'
    )
    
    evidence_ids = fields.Many2many(
        'ir.attachment',
        string='Evidence',
        help='Evidence of refusal (letters, emails, notes)'
    )
    
    days_stopped = fields.Integer(
        string='Days Clock Stopped',
        default=1,
        help='Number of days the deadline clock is stopped due to this refusal'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Logged By',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    notes = fields.Text(string='Notes')

