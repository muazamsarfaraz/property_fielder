# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ScheduleChangeRequest(models.Model):
    """Model to track schedule change requests from inspectors or property owners"""

    _name = 'property_fielder.change.request'
    _description = 'Schedule Change Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Info
    name = fields.Char(
        string='Request Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Request Type
    request_type = fields.Selection([
        ('reschedule', 'Reschedule Appointment'),
        ('cancel', 'Cancel Appointment'),
        ('change_inspector', 'Change Inspector'),
        ('change_time', 'Change Time Window'),
        ('other', 'Other'),
    ], string='Request Type', required=True, tracking=True)

    # Source
    requester_type = fields.Selection([
        ('inspector', 'Inspector'),
        ('owner', 'Property Owner'),
        ('internal', 'Internal'),
    ], string='Requester Type', required=True, tracking=True)

    requester_id = fields.Many2one(
        'res.partner',
        string='Requester',
        tracking=True,
        help='The person requesting the change'
    )

    # Job/Route Reference
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        tracking=True,
        help='The job to change'
    )

    route_id = fields.Many2one(
        'property_fielder.route',
        string='Route',
        related='job_id.route_id',
        store=True
    )

    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Current Inspector',
        related='job_id.inspector_id',
        store=True
    )

    # Request Details
    current_date = fields.Date(
        string='Current Date',
        related='job_id.scheduled_date',
        store=True
    )

    requested_date = fields.Date(
        string='Requested Date',
        help='New date requested (for reschedule requests)'
    )

    reason = fields.Text(
        string='Reason',
        required=True,
        help='Reason for the change request'
    )

    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal', tracking=True)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Resolution
    resolution_notes = fields.Text(
        string='Resolution Notes',
        help='Notes about how the request was resolved'
    )

    resolved_by = fields.Many2one(
        'res.users',
        string='Resolved By',
        readonly=True
    )

    resolved_date = fields.Datetime(
        string='Resolved Date',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate request number on create"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('property_fielder.change.request') or _('New')
        return super().create(vals_list)

    def action_submit(self):
        """Submit request for approval"""
        self.ensure_one()
        if not self.job_id:
            raise UserError(_('Please select a job for this change request.'))
        self.state = 'pending'
        # Notify relevant parties
        self._notify_pending()

    def action_approve(self):
        """Approve the change request"""
        self.ensure_one()
        self.write({
            'state': 'approved',
            'resolved_by': self.env.user.id,
            'resolved_date': fields.Datetime.now(),
        })
        # Apply the change
        self._apply_change()


    def _notify_pending(self):
        """Notify managers about pending request"""
        # Post message on job
        if self.job_id:
            self.job_id.message_post(
                body=_('Change request submitted: %s - %s') % (self.request_type, self.reason),
                subject=_('Schedule Change Request'),
                message_type='notification'
            )

    def _notify_rejected(self):
        """Notify requester that request was rejected"""
        if self.requester_id and self.requester_id.email:
            template = self.env.ref('property_fielder_field_service.email_template_change_request_rejected', raise_if_not_found=False)
            if template:
                template.send_mail(self.id, force_send=True)

    def _apply_change(self):
        """Apply the approved change"""
        if not self.job_id:
            return

        if self.request_type == 'reschedule' and self.requested_date:
            # Update job scheduled date
            self.job_id.write({
                'scheduled_date': self.requested_date,
                'route_id': False,  # Remove from current route
            })
            self.state = 'completed'

        elif self.request_type == 'cancel':
            # Cancel the job
            self.job_id.state = 'cancelled'
            self.state = 'completed'

        elif self.request_type == 'change_time':
            # Just mark as completed - time window changes need manual handling
            self.state = 'completed'

        # Post notification
        self.job_id.message_post(
            body=_('Change request approved and applied: %s') % self.request_type,
            subject=_('Schedule Updated'),
            message_type='notification'
        )

    def action_reject(self):
        """Reject the change request"""
        self.ensure_one()
        self.write({
            'state': 'rejected',
            'resolved_by': self.env.user.id,
            'resolved_date': fields.Datetime.now(),
        })
        # Notify requester
        self._notify_rejected()

    def action_cancel(self):
        """Cancel the change request"""
        self.state = 'cancelled'

