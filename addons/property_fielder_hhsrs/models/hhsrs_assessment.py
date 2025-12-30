# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HHSRSAssessment(models.Model):
    """HHSRS Assessment record with scoring calculation."""
    _name = 'property_fielder.hhsrs.assessment'
    _description = 'HHSRS Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assessment_date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    # Links
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    # Assessment Details
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
    
    # Hazard
    hhsrs_hazard_type_id = fields.Many2one(
        'property_fielder.hhsrs.hazard.type',
        string='Hazard Type',
        required=True,
        tracking=True
    )
    hazard_group = fields.Selection(
        related='hhsrs_hazard_type_id.group',
        string='Hazard Group',
        store=True
    )
    
    # Likelihood (16-band)
    likelihood_band_id = fields.Many2one(
        'property_fielder.hhsrs.likelihood.band',
        string='Likelihood Band',
        required=True,
        tracking=True,
        help='Select the likelihood of harm occurring in the next 12 months'
    )
    
    # Outcome Probabilities (must sum to 100%)
    outcome_prob_class_1 = fields.Float(
        string='Class I Outcome %',
        default=0,
        help='Extreme harm (death, permanent paralysis, etc.)'
    )
    outcome_prob_class_2 = fields.Float(
        string='Class II Outcome %',
        default=0,
        help='Severe harm (serious fractures, chronic illness)'
    )
    outcome_prob_class_3 = fields.Float(
        string='Class III Outcome %',
        default=0,
        help='Serious harm (broken limb, injury requiring hospital)'
    )
    outcome_prob_class_4 = fields.Float(
        string='Class IV Outcome %',
        default=100,
        help='Moderate harm (bruising, minor cuts)'
    )
    
    # Computed Score
    hhsrs_score = fields.Float(
        string='HHSRS Score',
        compute='_compute_hhsrs_score',
        store=True,
        digits=(10, 2)
    )
    hhsrs_band = fields.Selection([
        ('A', 'Band A (5000+)'),
        ('B', 'Band B (2000-4999)'),
        ('C', 'Band C (1000-1999)'),
        ('D', 'Band D (500-999)'),
        ('E', 'Band E (200-499)'),
        ('F', 'Band F (100-199)'),
        ('G', 'Band G (50-99)'),
        ('H', 'Band H (20-49)'),
        ('I', 'Band I (10-19)'),
        ('J', 'Band J (1-9)'),
    ], string='HHSRS Band', compute='_compute_hhsrs_score', store=True)
    
    hhsrs_category = fields.Selection([
        ('1', 'Category 1 (Serious)'),
        ('2', 'Category 2 (Less Serious)'),
    ], string='HHSRS Category', compute='_compute_hhsrs_score', store=True)
    
    # Justifications (tracked for audit)
    likelihood_justification = fields.Text(
        string='Likelihood Justification',
        tracking=True,
        help='Explain why this likelihood band was chosen'
    )
    outcome_justification = fields.Text(
        string='Outcome Justification',
        tracking=True,
        help='Explain the outcome probability distribution'
    )
    
    # Vulnerable Occupants
    vulnerable_occupant = fields.Boolean(string='Vulnerable Occupant Present')
    vulnerable_type = fields.Selection([
        ('elderly', 'Elderly (65+)'),
        ('child', 'Child (under 5)'),
        ('disabled', 'Disabled Person'),
        ('pregnant', 'Pregnant Woman'),
    ], string='Vulnerable Type')
    
    # Emergency
    is_emergency = fields.Boolean(
        string='Emergency Response Required',
        tracking=True,
        help='If True, triggers 24-hour Awaab\'s Law deadline'
    )
    
    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('superseded', 'Superseded'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Assessment Notes')
    
    # Photos
    photo_ids = fields.Many2many(
        'ir.attachment',
        string='Evidence Photos',
        help='Photos documenting the hazard'
    )

    # Outcome Weights (Housing Act 2004)
    OUTCOME_WEIGHTS = {1: 10000, 2: 1000, 3: 300, 4: 10}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'property_fielder.hhsrs.assessment'
                ) or _('New')
        return super().create(vals_list)

    @api.depends('likelihood_band_id', 'outcome_prob_class_1', 'outcome_prob_class_2',
                 'outcome_prob_class_3', 'outcome_prob_class_4')
    def _compute_hhsrs_score(self):
        """
        HHSRS Score = RSP × Σ (Outcome Weight × Outcome Probability)
        """
        for rec in self:
            if not rec.likelihood_band_id:
                rec.hhsrs_score = 0
                rec.hhsrs_band = 'J'
                rec.hhsrs_category = '2'
                continue

            rsp = rec.likelihood_band_id.rsp
            weighted_outcome = (
                (rec.outcome_prob_class_1 / 100) * self.OUTCOME_WEIGHTS[1] +
                (rec.outcome_prob_class_2 / 100) * self.OUTCOME_WEIGHTS[2] +
                (rec.outcome_prob_class_3 / 100) * self.OUTCOME_WEIGHTS[3] +
                (rec.outcome_prob_class_4 / 100) * self.OUTCOME_WEIGHTS[4]
            )
            rec.hhsrs_score = rsp * weighted_outcome

            # Assign band based on score
            score = rec.hhsrs_score
            if score >= 5000:
                rec.hhsrs_band, rec.hhsrs_category = 'A', '1'
            elif score >= 2000:
                rec.hhsrs_band, rec.hhsrs_category = 'B', '1'
            elif score >= 1000:
                rec.hhsrs_band, rec.hhsrs_category = 'C', '1'
            elif score >= 500:
                rec.hhsrs_band, rec.hhsrs_category = 'D', '2'
            elif score >= 200:
                rec.hhsrs_band, rec.hhsrs_category = 'E', '2'
            elif score >= 100:
                rec.hhsrs_band, rec.hhsrs_category = 'F', '2'
            elif score >= 50:
                rec.hhsrs_band, rec.hhsrs_category = 'G', '2'
            elif score >= 20:
                rec.hhsrs_band, rec.hhsrs_category = 'H', '2'
            elif score >= 10:
                rec.hhsrs_band, rec.hhsrs_category = 'I', '2'
            else:
                rec.hhsrs_band, rec.hhsrs_category = 'J', '2'

    @api.constrains('outcome_prob_class_1', 'outcome_prob_class_2',
                    'outcome_prob_class_3', 'outcome_prob_class_4')
    def _check_outcome_probabilities(self):
        """Outcome probabilities must sum to 100%."""
        for rec in self:
            total = (rec.outcome_prob_class_1 + rec.outcome_prob_class_2 +
                     rec.outcome_prob_class_3 + rec.outcome_prob_class_4)
            if abs(total - 100) > 0.01:
                raise ValidationError(
                    _("Outcome probabilities must sum to 100%%. Current total: %.1f%%") % total
                )

    def action_confirm(self):
        """Confirm the assessment."""
        self.write({'state': 'confirmed'})

    def action_supersede(self):
        """Mark as superseded by newer assessment."""
        self.write({'state': 'superseded'})

