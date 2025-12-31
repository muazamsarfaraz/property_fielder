# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class Defect(models.Model):
    """Unified defect record for regulatory faults and HHSRS hazards."""
    
    _name = 'property_fielder.defect'
    _description = 'Defect'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'deadline_date asc, create_date desc'
    
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    # Type classification
    defect_type = fields.Selection([
        ('regulatory_fault', 'Regulatory Fault'),
        ('hhsrs_hazard', 'HHSRS Hazard'),
    ], string='Defect Type', required=True, default='regulatory_fault', tracking=True)
    
    # Property link
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    # Source inspection
    inspection_id = fields.Many2one(
        'property_fielder.inspection',
        string='Source Inspection',
        ondelete='set null',
        help='Inspection that discovered this defect'
    )
    
    # Template response that created it
    response_id = fields.Many2one(
        'property_fielder.inspection.response',
        string='Source Response',
        ondelete='set null',
        help='Template response that created this defect'
    )
    
    # Fault code (for regulatory faults)
    fault_code_id = fields.Many2one(
        'property_fielder.fault.code',
        string='Fault Code',
        tracking=True,
        help='Industry standard fault code'
    )
    
    # HHSRS hazard type (for HHSRS hazards)
    hhsrs_hazard_type_id = fields.Many2one(
        'property_fielder.hhsrs.hazard.type',
        string='HHSRS Hazard Type',
        tracking=True,
        help='HHSRS hazard category (1-29)'
    )
    
    hhsrs_band = fields.Selection([
        ('band_a', 'Band A'),
        ('band_b', 'Band B'),
        ('band_c', 'Band C'),
        ('band_d', 'Band D'),
        ('band_e', 'Band E'),
        ('band_f', 'Band F'),
        ('band_g', 'Band G'),
        ('band_h', 'Band H'),
        ('band_i', 'Band I'),
        ('band_j', 'Band J'),
    ], string='HHSRS Band', tracking=True)
    
    # Severity
    severity_sla = fields.Selection([
        ('immediate', 'Immediate (24 hours)'),
        ('urgent', 'Urgent (7 days)'),
        ('standard', 'Standard (28 days)'),
        ('advisory', 'Advisory (No SLA)'),
    ], string='Severity', required=True, default='standard', tracking=True)
    
    # Description
    description = fields.Text(
        string='Description',
        required=True,
        help='Detailed description of the defect'
    )
    
    location = fields.Char(
        string='Location',
        help='Location within the property'
    )
    
    # Dates
    reported_date = fields.Date(
        string='Reported Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    
    deadline_date = fields.Date(
        string='Deadline Date',
        compute='_compute_deadline_date',
        store=True,
        tracking=True,
        help='SLA deadline for remediation'
    )
    
    fixed_date = fields.Date(
        string='Fixed Date',
        tracking=True,
        help='Date when defect was fixed'
    )
    
    verified_date = fields.Date(
        string='Verified Date',
        tracking=True,
        help='Date when fix was verified'
    )
    
    # Status workflow
    state = fields.Selection([
        ('reported', 'Reported'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('verified', 'Verified'),
        ('closed', 'Closed'),
    ], string='Status', default='reported', required=True, tracking=True)
    
    # SLA tracking
    is_breached = fields.Boolean(
        string='SLA Breached',
        compute='_compute_is_breached',
        store=True,
        help='True if deadline has passed without resolution'
    )
    
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_days_overdue',
        help='Number of days past deadline'
    )
    
    # Contractor assignment
    assigned_contractor_id = fields.Many2one(
        'res.partner',
        string='Assigned Contractor',
        domain=[('is_company', '=', True)],
        tracking=True
    )
    
    # Cost tracking
    estimated_cost = fields.Monetary(
        string='Estimated Cost',
        currency_field='currency_id'
    )
    
    actual_cost = fields.Monetary(
        string='Actual Cost',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    cost_approved = fields.Boolean(
        string='Cost Approved',
        default=False,
        tracking=True
    )

    cost_approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True
    )

    cost_approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True
    )

    # Tenant liability
    is_tenant_liable = fields.Boolean(
        string='Tenant Liable',
        default=False,
        help='Tenant is responsible for this defect'
    )

    tenant_liability_reason = fields.Text(
        string='Liability Reason',
        help='Reason for tenant liability'
    )

    # Photos
    photo_ids = fields.One2many(
        'property_fielder.defect.photo',
        'defect_id',
        string='Photos'
    )

    photo_count = fields.Integer(
        string='Photo Count',
        compute='_compute_photo_count'
    )

    # Access attempts
    access_attempt_ids = fields.One2many(
        'property_fielder.access.attempt',
        'defect_id',
        string='Access Attempts'
    )

    access_refused_count = fields.Integer(
        string='Access Refused Count',
        compute='_compute_access_refused',
        store=True
    )

    # Re-check inspection
    recheck_inspection_id = fields.Many2one(
        'property_fielder.inspection',
        string='Re-check Inspection',
        help='Inspection to verify the fix'
    )

    # Notes
    notes = fields.Text(string='Notes')

    # Constraints (Odoo 19 style)
    _check_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Defect reference must be unique!',
    )

    # ============================================================
    # COMPUTED FIELDS
    # ============================================================

    @api.depends('reported_date', 'severity_sla', 'fault_code_id.remediation_hours')
    def _compute_deadline_date(self):
        """Compute deadline based on severity SLA."""
        sla_hours = {
            'immediate': 24,
            'urgent': 168,
            'standard': 672,
            'advisory': 0,
        }
        for record in self:
            if record.severity_sla == 'advisory':
                record.deadline_date = False
            elif record.reported_date:
                hours = sla_hours.get(record.severity_sla, 672)
                record.deadline_date = record.reported_date + timedelta(hours=hours)
            else:
                record.deadline_date = False

    @api.depends('deadline_date', 'state')
    def _compute_is_breached(self):
        """Check if SLA is breached."""
        today = fields.Date.today()
        for record in self:
            if record.state in ['fixed', 'verified', 'closed']:
                record.is_breached = False
            elif record.deadline_date and today > record.deadline_date:
                record.is_breached = True
            else:
                record.is_breached = False

    def _compute_days_overdue(self):
        """Compute days overdue."""
        today = fields.Date.today()
        for record in self:
            if record.deadline_date and today > record.deadline_date:
                record.days_overdue = (today - record.deadline_date).days
            else:
                record.days_overdue = 0

    @api.depends('photo_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photo_ids)

    @api.depends('access_attempt_ids.result')
    def _compute_access_refused(self):
        for record in self:
            record.access_refused_count = len(record.access_attempt_ids.filtered(
                lambda a: a.result == 'refused'
            ))

    # ============================================================
    # CRUD OVERRIDES
    # ============================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'property_fielder.defect'
                ) or _('New')
        return super().create(vals_list)

    # ============================================================
    # ACTIONS
    # ============================================================

    def action_acknowledge(self):
        """Acknowledge the defect."""
        self.write({'state': 'acknowledged'})

    def action_start_work(self):
        """Start remediation work."""
        self.write({'state': 'in_progress'})

    def action_mark_fixed(self):
        """Mark defect as fixed."""
        self.write({
            'state': 'fixed',
            'fixed_date': fields.Date.today(),
        })

    def action_verify(self):
        """Verify the fix."""
        self.write({
            'state': 'verified',
            'verified_date': fields.Date.today(),
        })

    def action_close(self):
        """Close the defect."""
        self.write({'state': 'closed'})

    def action_approve_cost(self):
        """Approve the estimated cost."""
        self.write({
            'cost_approved': True,
            'cost_approved_by': self.env.user.id,
            'cost_approved_date': fields.Datetime.now(),
        })

    def action_view_photos(self):
        """View defect photos."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Defect Photos'),
            'res_model': 'property_fielder.defect.photo',
            'view_mode': 'kanban,tree,form',
            'domain': [('defect_id', '=', self.id)],
            'context': {'default_defect_id': self.id},
        }

    def action_schedule_recheck(self):
        """Schedule a re-check inspection."""
        self.ensure_one()
        # This would create a new inspection linked to this defect
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Re-check'),
            'res_model': 'property_fielder.inspection',
            'view_mode': 'form',
            'context': {
                'default_property_id': self.property_id.id,
                'default_is_recheck': True,
                'default_original_defect_id': self.id,
            },
        }

    def action_assign_contractor(self):
        """Open wizard to assign a contractor and send notification."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assign Contractor'),
            'res_model': 'property_fielder.assign.contractor.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_defect_id': self.id,
                'default_contractor_id': self.assigned_contractor_id.id,
            },
        }

    def _send_contractor_assignment_notification(self):
        """Send email notification to assigned contractor."""
        self.ensure_one()
        if not self.assigned_contractor_id:
            return False

        if not self.assigned_contractor_id.email:
            self.message_post(
                body=_('Cannot send notification: Contractor %s has no email address.') % (
                    self.assigned_contractor_id.name
                ),
                message_type='notification'
            )
            return False

        template = self.env.ref(
            'property_fielder_defects.email_template_contractor_assignment',
            raise_if_not_found=False
        )

        if template:
            template.send_mail(self.id, force_send=True)
            self.message_post(
                body=_('Notification sent to contractor: %s (%s)') % (
                    self.assigned_contractor_id.name,
                    self.assigned_contractor_id.email
                ),
                message_type='notification'
            )
            return True
        else:
            # Fallback: post to chatter
            self.message_post(
                body=_('Contractor assignment email template not found. '
                       'Please create template: property_fielder_defects.email_template_contractor_assignment'),
                message_type='notification'
            )
            return False

    def write(self, vals):
        """Override write to send contractor notification on assignment."""
        result = super().write(vals)

        # Check if contractor was just assigned
        if 'assigned_contractor_id' in vals and vals['assigned_contractor_id']:
            for record in self:
                record._send_contractor_assignment_notification()

        return result

