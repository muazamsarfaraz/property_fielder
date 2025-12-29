# -*- coding: utf-8 -*-
from odoo import models, fields, api


class KeyHistory(models.Model):
    _name = 'property_fielder.key.history'
    _description = 'Key Set History'
    _order = 'create_date desc'

    key_set_id = fields.Many2one(
        'property_fielder.key.set',
        string='Key Set',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    action_type = fields.Selection([
        ('checkout', 'Checked Out'),
        ('return', 'Returned'),
        ('transfer', 'Transferred'),
        ('lost', 'Reported Lost'),
        ('found', 'Found'),
        ('created', 'Created'),
        ('destroyed', 'Destroyed')
    ], string='Action', required=True)
    
    holder_id = fields.Many2one(
        'res.partner',
        string='Key Holder',
        help='The person/company who received or returned the keys'
    )
    
    performed_by_id = fields.Many2one(
        'res.partner',
        string='Performed By',
        help='User who performed this action'
    )
    
    notes = fields.Text(string='Notes')
    
    # Related property for easy access
    property_id = fields.Many2one(
        related='key_set_id.property_id',
        store=True,
        string='Property'
    )

