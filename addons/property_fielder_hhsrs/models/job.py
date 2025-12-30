# -*- coding: utf-8 -*-
from odoo import models, fields


class JobHHSRS(models.Model):
    """Extend Job model with HHSRS-specific fields.
    
    This adds the HHSRS Assessment and Awaab's Law deadline linking
    to jobs when the HHSRS module is installed.
    """
    _inherit = 'property_fielder.job'

    hhsrs_assessment_id = fields.Many2one(
        'property_fielder.hhsrs.assessment',
        string='HHSRS Assessment',
        help='Source HHSRS assessment for remediation jobs'
    )
    awaab_deadline_id = fields.Many2one(
        'property_fielder.awaab.deadline',
        string='Awaab Deadline',
        help="Linked Awaab's Law deadline"
    )

