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

    # ============================================================
    # REMEDIATION JOB INTEGRATION
    # ============================================================

    remediation_job_id = fields.Many2one(
        'property_fielder.job',
        string='Remediation Job',
        readonly=True,
        help='Field service job created for hazard remediation'
    )
    remediation_required = fields.Boolean(
        string='Remediation Required',
        compute='_compute_remediation_required',
        store=True,
        help='Whether remediation is required based on hazard category'
    )
    remediation_type = fields.Selection([
        ('repair', 'Repair'),
        ('replacement', 'Replacement'),
        ('removal', 'Removal'),
        ('monitoring', 'Monitoring Only'),
    ], string='Remediation Type', tracking=True)
    estimated_cost = fields.Monetary(
        string='Estimated Cost',
        currency_field='currency_id',
        help='Estimated cost of remediation'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    remediation_job_count = fields.Integer(
        string='Remediation Jobs',
        compute='_compute_remediation_job_count'
    )

    # Outcome Weights (Housing Act 2004)
    OUTCOME_WEIGHTS = {1: 10000, 2: 1000, 3: 300, 4: 10}

    @api.depends('hhsrs_category', 'hhsrs_band')
    def _compute_remediation_required(self):
        """Determine if remediation is required based on hazard category."""
        for rec in self:
            # Cat 1 always requires remediation
            # Cat 2 with bands D, E, F also require remediation
            if rec.hhsrs_category == '1':
                rec.remediation_required = True
            elif rec.hhsrs_category == '2' and rec.hhsrs_band in ['D', 'E', 'F']:
                rec.remediation_required = True
            else:
                rec.remediation_required = False

    def _compute_remediation_job_count(self):
        """Count remediation jobs."""
        for rec in self:
            rec.remediation_job_count = 1 if rec.remediation_job_id else 0

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
        """Confirm the assessment and create remediation job if needed."""
        self.ensure_one()
        self.write({'state': 'confirmed'})

        # Create remediation job for Cat 1 hazards (emergency)
        if self.hhsrs_category == '1':
            self._create_remediation_job(priority='3', is_emergency=True)
        # Create remediation job for Cat 2 hazards with bands D, E, F (scheduled)
        elif self.hhsrs_category == '2' and self.hhsrs_band in ['D', 'E', 'F']:
            self._create_remediation_job(priority='2', is_emergency=False)

    def _create_remediation_job(self, priority='1', is_emergency=False):
        """Create a field service job for hazard remediation."""
        from datetime import timedelta

        self.ensure_one()

        # Skip if job already exists
        if self.remediation_job_id:
            return self.remediation_job_id

        # Calculate deadline
        deadline = self._get_remediation_deadline(is_emergency)

        # Build job values
        job_vals = {
            'name': _('HHSRS Remediation: %s') % self.hhsrs_hazard_type_id.name,
            'property_id': self.property_id.id,
            'partner_id': self.property_id.partner_id.id if self.property_id.partner_id else False,
            'job_type': 'remediation',
            'priority': priority,
            'is_hhsrs_remediation': True,
            'hhsrs_assessment_id': self.id,
            'scheduled_date': deadline,
            'notes': self._build_remediation_notes(),
            'duration_minutes': 120,  # Default 2 hours for remediation
            'latitude': self.property_id.latitude,
            'longitude': self.property_id.longitude,
            'street': self.property_id.street,
            'city': self.property_id.city,
            'zip': self.property_id.zip,
        }

        job = self.env['property_fielder.job'].create(job_vals)
        self.remediation_job_id = job.id

        # Link to Awaab deadline if applicable
        if self.hhsrs_hazard_type_id.is_awaab_covered:
            self._create_awaab_deadline(job, is_emergency)

        self.message_post(
            body=_('Remediation job %s created with priority %s') % (job.name, priority),
            message_type='notification'
        )

        return job

    def _get_remediation_deadline(self, is_emergency):
        """Calculate deadline based on hazard category."""
        from datetime import timedelta

        if is_emergency:
            return fields.Date.today()  # Same day for Cat 1
        else:
            # Reasonable time from config parameter
            days = int(self.env['ir.config_parameter'].sudo().get_param(
                'property_fielder_hhsrs.awaab_reasonable_time_days', '28'
            ))
            return fields.Date.today() + timedelta(days=days)

    def _build_remediation_notes(self):
        """Build notes for remediation job."""
        notes = []
        notes.append(_('HHSRS Assessment: %s') % self.name)
        notes.append(_('Hazard: %s') % self.hhsrs_hazard_type_id.name)
        notes.append(_('Category: %s') % self.hhsrs_category)
        notes.append(_('Band: %s') % self.hhsrs_band)
        notes.append(_('Score: %.2f') % self.hhsrs_score)
        if self.vulnerable_occupant:
            notes.append(_('⚠️ Vulnerable Occupant: %s') % dict(self._fields['vulnerable_type'].selection).get(self.vulnerable_type, ''))
        if self.is_emergency:
            notes.append(_('🚨 EMERGENCY RESPONSE REQUIRED'))
        if self.notes:
            notes.append(_('Assessment Notes: %s') % self.notes)
        return '\n'.join(notes)

    def _create_awaab_deadline(self, job, is_emergency):
        """Create Awaab deadline linked to remediation job."""
        hazard_type = 'emergency' if is_emergency else 'non_emergency'

        # Check if this is a damp/mould hazard
        if self.hhsrs_hazard_type_id.code in ['damp', 'mould', 'damp_mould']:
            hazard_type = 'damp_mould'

        deadline = self.env['property_fielder.awaab.deadline'].create({
            'property_id': self.property_id.id,
            'hhsrs_assessment_id': self.id,
            'hazard_type': hazard_type,
            'report_date': fields.Date.today(),
        })

        # Link job to deadline
        job.awaab_deadline_id = deadline.id

        return deadline

    def action_view_remediation_job(self):
        """Open the remediation job."""
        self.ensure_one()
        if self.remediation_job_id:
            return {
                'name': _('Remediation Job'),
                'type': 'ir.actions.act_window',
                'res_model': 'property_fielder.job',
                'view_mode': 'form',
                'res_id': self.remediation_job_id.id,
            }
        else:
            # Create job if it doesn't exist
            if self.remediation_required:
                is_emergency = self.hhsrs_category == '1'
                priority = '3' if is_emergency else '2'
                self._create_remediation_job(priority=priority, is_emergency=is_emergency)
                return self.action_view_remediation_job()
            return {'type': 'ir.actions.act_window_close'}

    def action_supersede(self):
        """Mark as superseded by newer assessment."""
        self.write({'state': 'superseded'})

