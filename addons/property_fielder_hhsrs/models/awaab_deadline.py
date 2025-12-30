# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta


class AwaabDeadline(models.Model):
    """Awaab's Law deadline tracking."""
    _name = 'property_fielder.awaab.deadline'
    _description = 'Awaab\'s Law Deadline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'completion_deadline asc, id desc'

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True
    )
    
    # Links
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    hhsrs_assessment_id = fields.Many2one(
        'property_fielder.hhsrs.assessment',
        string='HHSRS Assessment',
        ondelete='set null'
    )
    damp_mould_id = fields.Many2one(
        'property_fielder.damp.mould',
        string='Damp & Mould Case',
        ondelete='set null'
    )
    
    # Hazard Type
    hazard_type = fields.Selection([
        ('emergency', 'Emergency (24 hours)'),
        ('non_emergency', 'Non-Emergency (7/14 days)'),
        ('damp_mould', 'Damp & Mould (Awaab Specific)'),
    ], string='Hazard Type', required=True, tracking=True)
    
    # Report Date
    report_date = fields.Date(
        string='Report Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    # Investigation Deadline
    investigation_deadline = fields.Date(
        string='Investigation Deadline',
        compute='_compute_deadlines',
        store=True
    )
    investigation_date = fields.Date(string='Investigation Date')
    investigation_met = fields.Boolean(
        string='Investigation Met',
        compute='_compute_deadline_status',
        store=True
    )
    
    # Repairs Start Deadline
    repairs_start_deadline = fields.Date(
        string='Repairs Start Deadline',
        compute='_compute_deadlines',
        store=True
    )
    repairs_start_date = fields.Date(string='Repairs Start Date')
    repairs_start_met = fields.Boolean(
        string='Repairs Start Met',
        compute='_compute_deadline_status',
        store=True
    )
    
    # Completion Deadline
    completion_deadline = fields.Date(
        string='Completion Deadline',
        compute='_compute_deadlines',
        store=True
    )
    completion_date = fields.Date(string='Completion Date')
    completion_met = fields.Boolean(
        string='Completion Met',
        compute='_compute_deadline_status',
        store=True
    )
    
    # State
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', tracking=True, compute='_compute_state', store=True)
    
    # Breach Tracking
    breach_count = fields.Integer(
        string='Breach Count',
        compute='_compute_breach_count',
        store=True
    )
    
    # Tenant Notifications
    tenant_notified_investigation = fields.Boolean(string='Tenant Notified (Investigation)')
    tenant_notified_schedule = fields.Boolean(string='Tenant Notified (Schedule)')
    
    # Access Refusals (stops the clock)
    access_refusal_ids = fields.One2many(
        'property_fielder.awaab.access.refusal',
        'deadline_id',
        string='Access Refusals'
    )
    total_days_stopped = fields.Integer(
        string='Total Days Clock Stopped',
        compute='_compute_total_days_stopped',
        store=True
    )
    
    notes = fields.Text(string='Notes')

    @api.depends('property_id', 'hazard_type', 'report_date')
    def _compute_name(self):
        for rec in self:
            prop = rec.property_id.name or 'Unknown'
            htype = dict(self._fields['hazard_type'].selection).get(rec.hazard_type, '')
            date = rec.report_date or ''
            rec.name = f"AWAAB/{prop}/{htype}/{date}"

    @api.depends('hazard_type', 'report_date', 'investigation_date', 'total_days_stopped')
    def _compute_deadlines(self):
        """Calculate deadlines based on hazard type."""
        reasonable_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'property_fielder_hhsrs.awaab_reasonable_time_days', '28'
        ))
        
        for rec in self:
            if not rec.report_date:
                rec.investigation_deadline = False
                rec.repairs_start_deadline = False
                rec.completion_deadline = False
                continue
                
            stopped = rec.total_days_stopped or 0
            
            if rec.hazard_type == 'emergency':
                # Emergency: 24 hours for everything
                rec.investigation_deadline = rec.report_date + timedelta(days=1 + stopped)
                rec.repairs_start_deadline = rec.report_date + timedelta(days=1 + stopped)
                rec.completion_deadline = rec.report_date + timedelta(days=1 + stopped)
            elif rec.hazard_type == 'damp_mould':
                # Damp & Mould: 14 days investigation, 7 days to start, reasonable to complete
                rec.investigation_deadline = rec.report_date + timedelta(days=14 + stopped)
                rec.repairs_start_deadline = rec.report_date + timedelta(days=21 + stopped)
                rec.completion_deadline = rec.report_date + timedelta(days=21 + reasonable_days + stopped)
            else:
                # Non-emergency: 14 days investigation, 7 days to start, reasonable to complete
                rec.investigation_deadline = rec.report_date + timedelta(days=14 + stopped)
                rec.repairs_start_deadline = rec.report_date + timedelta(days=21 + stopped)
                rec.completion_deadline = rec.report_date + timedelta(days=21 + reasonable_days + stopped)

    @api.depends('investigation_date', 'investigation_deadline',
                 'repairs_start_date', 'repairs_start_deadline',
                 'completion_date', 'completion_deadline')
    def _compute_deadline_status(self):
        """Check if each deadline was met."""
        for rec in self:
            # Investigation
            if rec.investigation_date and rec.investigation_deadline:
                rec.investigation_met = rec.investigation_date <= rec.investigation_deadline
            else:
                rec.investigation_met = False

            # Repairs Start
            if rec.repairs_start_date and rec.repairs_start_deadline:
                rec.repairs_start_met = rec.repairs_start_date <= rec.repairs_start_deadline
            else:
                rec.repairs_start_met = False

            # Completion
            if rec.completion_date and rec.completion_deadline:
                rec.completion_met = rec.completion_date <= rec.completion_deadline
            else:
                rec.completion_met = False

    @api.depends('investigation_met', 'repairs_start_met', 'completion_met',
                 'completion_date', 'investigation_deadline', 'repairs_start_deadline',
                 'completion_deadline')
    def _compute_breach_count(self):
        """Count number of deadline breaches."""
        for rec in self:
            breaches = 0
            today = fields.Date.today()

            if rec.investigation_deadline and not rec.investigation_met:
                if rec.investigation_date or today > rec.investigation_deadline:
                    breaches += 1

            if rec.repairs_start_deadline and not rec.repairs_start_met:
                if rec.repairs_start_date or today > rec.repairs_start_deadline:
                    breaches += 1

            if rec.completion_deadline and not rec.completion_met:
                if rec.completion_date or today > rec.completion_deadline:
                    breaches += 1

            rec.breach_count = breaches

    @api.depends('completion_date', 'investigation_deadline', 'repairs_start_deadline',
                 'completion_deadline', 'breach_count')
    def _compute_state(self):
        """Compute overall state."""
        today = fields.Date.today()
        for rec in self:
            if rec.completion_date:
                rec.state = 'completed'
            elif rec.breach_count > 0:
                rec.state = 'overdue'
            elif rec.repairs_start_date or rec.investigation_date:
                rec.state = 'in_progress'
            else:
                rec.state = 'pending'

    @api.depends('access_refusal_ids.days_stopped')
    def _compute_total_days_stopped(self):
        for rec in self:
            rec.total_days_stopped = sum(rec.access_refusal_ids.mapped('days_stopped'))

    def _cron_check_awaab_deadlines(self):
        """Daily cron to check Awaab deadlines and send alerts."""
        today = fields.Date.today()
        warning_days = 2

        deadlines = self.search([
            ('state', 'not in', ['completed', 'cancelled']),
        ])

        for deadline in deadlines:
            # Check investigation deadline
            if deadline.investigation_deadline and not deadline.investigation_met:
                days_until = (deadline.investigation_deadline - today).days
                if days_until <= 0:
                    deadline._send_breach_alert('investigation')
                elif days_until <= warning_days:
                    deadline._send_warning_alert('investigation', days_until)

            # Check repairs start deadline
            if deadline.repairs_start_deadline and not deadline.repairs_start_met:
                days_until = (deadline.repairs_start_deadline - today).days
                if days_until <= 0:
                    deadline._send_breach_alert('repairs_start')
                elif days_until <= warning_days:
                    deadline._send_warning_alert('repairs_start', days_until)

            # Check completion deadline
            if deadline.completion_deadline and not deadline.completion_met:
                days_until = (deadline.completion_deadline - today).days
                if days_until <= 0:
                    deadline._send_breach_alert('completion')
                elif days_until <= warning_days:
                    deadline._send_warning_alert('completion', days_until)

    def _send_breach_alert(self, deadline_type):
        """Send breach notification and create activity."""
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=fields.Date.today(),
            summary=_("URGENT: Awaab's Law %s Deadline BREACHED") % deadline_type.replace('_', ' ').title(),
            note=_("Property: %s\nHazard Type: %s\nDeadline breached on: %s") % (
                self.property_id.name,
                self.hazard_type,
                fields.Date.today()
            ),
        )

    def _send_warning_alert(self, deadline_type, days_remaining):
        """Send warning notification."""
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=fields.Date.today() + timedelta(days=days_remaining),
            summary=_("WARNING: Awaab's Law %s Deadline in %d days") % (
                deadline_type.replace('_', ' ').title(), days_remaining
            ),
        )
