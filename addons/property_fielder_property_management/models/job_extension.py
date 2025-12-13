# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FieldServiceJobExtension(models.Model):
    """Extend Field Service Job model to add property link"""
    
    _inherit = 'property_fielder.job'
    
    # Property Link (for property inspection jobs)
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        tracking=True,
        ondelete='set null',
        help='Property to be inspected (if this is a property inspection job)'
    )

