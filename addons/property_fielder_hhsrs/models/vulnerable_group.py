# -*- coding: utf-8 -*-
from odoo import models, fields


class HHSRSVulnerableGroup(models.Model):
    """Vulnerable groups for HHSRS assessments."""
    _name = 'property_fielder.hhsrs.vulnerable.group'
    _description = 'HHSRS Vulnerable Group'
    _order = 'sequence, name'

    name = fields.Char(string='Group Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)

    # Constraints (Odoo 19 style)
    _check_code_unique = models.Constraint(
        'UNIQUE(code)',
        'Vulnerable group code must be unique!',
    )

