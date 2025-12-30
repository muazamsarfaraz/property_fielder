# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HHSRSHazardType(models.Model):
    """29 HHSRS hazard categories (reference data)."""
    _name = 'property_fielder.hhsrs.hazard.type'
    _description = 'HHSRS Hazard Type'
    _order = 'sequence, code'

    name = fields.Char(string='Hazard Name', required=True, translate=True)
    code = fields.Char(string='Hazard Code', required=True, help='e.g., A1, B2, C3')
    
    group = fields.Selection([
        ('physiological', 'A. Physiological Requirements'),
        ('psychological', 'B. Psychological Requirements'),
        ('protection', 'C. Protection Against Accidents'),
        ('infection', 'D. Protection Against Infection'),
    ], string='Hazard Group', required=True)
    
    description = fields.Text(string='Description', translate=True)
    assessment_guide = fields.Text(
        string='Assessment Guide',
        help='How to assess this hazard during inspection'
    )
    typical_remedies = fields.Text(
        string='Typical Remedies',
        help='Common remedial actions for this hazard'
    )
    
    # Awaab's Law
    is_awaab_covered = fields.Boolean(
        string='Covered by Awaab\'s Law',
        default=False,
        help='If True, this hazard triggers Awaab\'s Law deadlines'
    )
    
    # Display
    sequence = fields.Integer(string='Sequence', default=10)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Hazard code must be unique!'),
    ]

