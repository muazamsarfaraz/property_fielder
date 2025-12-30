# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DHSAssessment(models.Model):
    """Decent Homes Standard 4-criteria assessment."""
    _name = 'property_fielder.dhs.assessment'
    _description = 'Decent Homes Standard Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assessment_date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    # Property
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    # Assessment
    assessment_date = fields.Date(
        string='Assessment Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    assessor_id = fields.Many2one(
        'res.users',
        string='Assessor',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    # Criterion A: Statutory Minimum (Free from Category 1 hazards)
    criterion_a_met = fields.Boolean(
        string='A: Statutory Minimum',
        help='Free from Category 1 HHSRS hazards',
        tracking=True
    )
    criterion_a_auto = fields.Boolean(
        string='A: Auto-Check',
        compute='_compute_criterion_a_auto',
        store=True,
        help='Automatically calculated from active HHSRS assessments'
    )
    criterion_a_note = fields.Char(string='Criterion A Note')
    
    # Criterion B: Reasonable State of Repair
    criterion_b_met = fields.Boolean(
        string='B: Reasonable State of Repair',
        help='Building components in reasonable repair',
        tracking=True
    )
    criterion_b_auto = fields.Boolean(
        string='B: Auto-Check',
        compute='_compute_criterion_b_auto',
        store=True,
        help='Automatically calculated from building components'
    )
    criterion_b_note = fields.Char(string='Criterion B Note')
    
    # Criterion C: Modern Facilities & Services
    criterion_c_met = fields.Boolean(
        string='C: Modern Facilities & Services',
        help='Reasonably modern facilities and services',
        tracking=True
    )
    criterion_c_note = fields.Char(string='Criterion C Note')
    
    # Criterion D: Thermal Comfort
    criterion_d_met = fields.Boolean(
        string='D: Thermal Comfort',
        help='Efficient heating and effective insulation (EPC E or better)',
        tracking=True
    )
    criterion_d_auto = fields.Boolean(
        string='D: Auto-Check',
        compute='_compute_criterion_d_auto',
        store=True,
        help='Automatically calculated from EPC rating'
    )
    criterion_d_note = fields.Char(string='Criterion D Note')
    
    # Overall Result
    is_decent = fields.Boolean(
        string='Is Decent',
        compute='_compute_is_decent',
        store=True,
        help='True if all 4 criteria are met'
    )
    
    # Remediation
    remediation_plan = fields.Text(
        string='Remediation Plan',
        help='Plan to achieve decent homes status'
    )
    target_date = fields.Date(
        string='Target Date',
        help='Target date to achieve decent status'
    )
    
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'property_fielder.dhs.assessment'
                ) or _('New')
        return super().create(vals_list)

    @api.depends('property_id')
    def _compute_criterion_a_auto(self):
        """Criterion A: Free from Category 1 Hazards."""
        HHSRSAssessment = self.env['property_fielder.hhsrs.assessment']
        for rec in self:
            if not rec.property_id:
                rec.criterion_a_auto = False
                continue
            # Check for any confirmed Cat 1 hazards
            cat1_assessments = HHSRSAssessment.search([
                ('property_id', '=', rec.property_id.id),
                ('state', '=', 'confirmed'),
                ('hhsrs_category', '=', '1'),
            ])
            rec.criterion_a_auto = len(cat1_assessments) == 0

    @api.depends('property_id')
    def _compute_criterion_b_auto(self):
        """Criterion B: Reasonable State of Repair."""
        Component = self.env['property_fielder.building.component']
        for rec in self:
            if not rec.property_id:
                rec.criterion_b_auto = False
                continue
            # Check for critical/failed components
            failing = Component.search([
                ('property_id', '=', rec.property_id.id),
                '|',
                ('condition', '=', 'critical'),
                ('is_beyond_life', '=', True),
            ])
            rec.criterion_b_auto = len(failing) == 0

    @api.depends('property_id.epc_rating')
    def _compute_criterion_d_auto(self):
        """Criterion D: Thermal Comfort (EPC E or better)."""
        PASSING_RATINGS = ['A', 'B', 'C', 'D', 'E']
        for rec in self:
            if rec.property_id and rec.property_id.epc_rating:
                rec.criterion_d_auto = rec.property_id.epc_rating in PASSING_RATINGS
            else:
                rec.criterion_d_auto = False
                rec.criterion_d_note = 'EPC rating required'

    @api.depends('criterion_a_met', 'criterion_b_met', 'criterion_c_met', 'criterion_d_met')
    def _compute_is_decent(self):
        """Property is decent if all 4 criteria are met."""
        for rec in self:
            rec.is_decent = all([
                rec.criterion_a_met,
                rec.criterion_b_met,
                rec.criterion_c_met,
                rec.criterion_d_met,
            ])
