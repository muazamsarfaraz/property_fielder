# -*- coding: utf-8 -*-
from odoo import models, fields


class HHSRSLikelihoodBand(models.Model):
    """Official 16 HHSRS Likelihood Bands with Representative Scale Points (RSP)."""
    _name = 'property_fielder.hhsrs.likelihood.band'
    _description = 'HHSRS Likelihood Band'
    _order = 'sequence'

    name = fields.Char(string='Band Name', required=True, help='e.g., "1 in 18"')
    code = fields.Char(string='Band Code', required=True, help='L1-L16')
    ratio = fields.Char(string='Ratio', help='Ratio description e.g., "1 in 1"')
    
    rsp = fields.Float(
        string='Representative Scale Point',
        digits=(10, 6),
        required=True,
        help='RSP value used in HHSRS score calculation'
    )
    
    description = fields.Char(string='Description', help='e.g., Certain, Very High, High')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)

    # Constraints (Odoo 19 style)
    _check_code_unique = models.Constraint(
        'UNIQUE(code)',
        'Likelihood band code must be unique!',
    )

