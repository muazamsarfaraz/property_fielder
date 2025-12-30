# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DampMould(models.Model):
    """Damp and mould tracking (Awaab's Law focus)."""
    _name = 'property_fielder.damp.mould'
    _description = 'Damp & Mould Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reported_date desc, id desc'

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
    
    # Reporting
    reported_date = fields.Date(
        string='Reported Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    reported_by = fields.Many2one(
        'res.partner',
        string='Reported By',
        help='Tenant or person who reported the issue'
    )
    
    # Location & Details
    location = fields.Char(
        string='Location',
        help='Specific location (room, wall, ceiling)'
    )
    
    severity = fields.Selection([
        ('minor', 'Minor (Surface mould, small area)'),
        ('moderate', 'Moderate (Visible mould, larger area)'),
        ('severe', 'Severe (Extensive mould, structural damp)'),
    ], string='Severity', required=True, default='minor', tracking=True)
    
    cause = fields.Selection([
        ('condensation', 'Condensation'),
        ('penetrating', 'Penetrating Damp'),
        ('rising', 'Rising Damp'),
        ('leak', 'Water Leak'),
        ('unknown', 'Unknown'),
    ], string='Cause', default='unknown')
    
    cause_identified = fields.Boolean(string='Root Cause Identified')
    cause_date = fields.Date(string='Cause Identified Date')
    
    # State
    state = fields.Selection([
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('repairs_started', 'Repairs Started'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='reported', tracking=True)
    
    # Habitability
    is_uninhabitable = fields.Boolean(
        string='Property Uninhabitable',
        help='If True, property is not safe for habitation'
    )
    
    # Decant
    decant_required = fields.Boolean(string='Decant Required')
    decant_arranged = fields.Boolean(string='Decant Arranged')
    decant_property_id = fields.Many2one(
        'property_fielder.property',
        string='Temporary Accommodation'
    )
    decant_date_start = fields.Date(string='Decant Start Date')
    decant_date_end = fields.Date(string='Decant End Date')
    
    # Linked Records
    awaab_deadline_id = fields.Many2one(
        'property_fielder.awaab.deadline',
        string='Awaab Deadline',
        ondelete='set null'
    )
    hhsrs_assessment_id = fields.Many2one(
        'property_fielder.hhsrs.assessment',
        string='HHSRS Assessment',
        ondelete='set null'
    )
    
    awaab_compliant = fields.Boolean(
        string='Awaab Compliant',
        compute='_compute_awaab_compliant',
        store=True
    )
    
    # Evidence
    photo_ids = fields.Many2many(
        'ir.attachment',
        string='Evidence Photos'
    )
    
    # Timeline
    timeline_ids = fields.One2many(
        'property_fielder.damp.mould.timeline',
        'damp_mould_id',
        string='Timeline'
    )
    
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'property_fielder.damp.mould'
                ) or _('New')
        records = super().create(vals_list)
        # Auto-create Awaab deadline
        for rec in records:
            rec._create_awaab_deadline()
        return records

    def _create_awaab_deadline(self):
        """Create an Awaab deadline for this damp/mould case."""
        self.ensure_one()
        if not self.awaab_deadline_id:
            deadline = self.env['property_fielder.awaab.deadline'].create({
                'property_id': self.property_id.id,
                'hazard_type': 'damp_mould',
                'report_date': self.reported_date,
                'damp_mould_id': self.id,
            })
            self.awaab_deadline_id = deadline.id

    @api.depends('awaab_deadline_id.breach_count')
    def _compute_awaab_compliant(self):
        for rec in self:
            if rec.awaab_deadline_id:
                rec.awaab_compliant = rec.awaab_deadline_id.breach_count == 0
            else:
                rec.awaab_compliant = True

    def action_start_investigation(self):
        self.write({'state': 'investigating'})
        self._log_timeline('investigated', 'Investigation started')

    def action_start_repairs(self):
        self.write({'state': 'repairs_started'})
        self._log_timeline('repairs_started', 'Repairs commenced')

    def action_resolve(self):
        self.write({'state': 'resolved'})
        self._log_timeline('completed', 'Issue resolved')

    def _log_timeline(self, event_type, description):
        self.env['property_fielder.damp.mould.timeline'].create({
            'damp_mould_id': self.id,
            'event_type': event_type,
            'description': description,
        })


class DampMouldTimeline(models.Model):
    """Timeline events for damp/mould cases."""
    _name = 'property_fielder.damp.mould.timeline'
    _description = 'Damp & Mould Timeline Event'
    _order = 'date desc'

    damp_mould_id = fields.Many2one(
        'property_fielder.damp.mould',
        string='Damp & Mould Case',
        required=True,
        ondelete='cascade'
    )

    date = fields.Datetime(
        string='Date/Time',
        required=True,
        default=fields.Datetime.now
    )

    event_type = fields.Selection([
        ('reported', 'Reported'),
        ('investigated', 'Investigated'),
        ('repairs_started', 'Repairs Started'),
        ('completed', 'Completed'),
        ('tenant_contact', 'Tenant Contact'),
        ('photo_added', 'Photo Added'),
        ('note', 'Note'),
    ], string='Event Type', required=True)

    description = fields.Text(string='Description')

    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True
    )

    photo_ids = fields.Many2many(
        'ir.attachment',
        string='Photos'
    )
