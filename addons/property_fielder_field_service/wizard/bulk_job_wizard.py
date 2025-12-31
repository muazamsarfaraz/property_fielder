# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BulkJobWizard(models.TransientModel):
    """Wizard for bulk job operations"""

    _name = 'property_fielder.bulk.job.wizard'
    _description = 'Bulk Job Operations Wizard'

    # Operation selection
    operation = fields.Selection([
        ('update_status', 'Update Status'),
        ('assign_inspector', 'Assign Inspector'),
        ('reschedule', 'Reschedule'),
        ('send_notifications', 'Send Notifications'),
        ('cancel', 'Cancel Jobs'),
    ], string='Operation', required=True, default='update_status')

    # Job selection
    job_ids = fields.Many2many(
        'property_fielder.job',
        'bulk_job_wizard_job_rel',
        'wizard_id',
        'job_id',
        string='Jobs',
        required=True
    )

    # Status update fields
    new_state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='New Status')

    # Inspector assignment
    inspector_id = fields.Many2one('res.partner', string='Inspector', domain=[('is_inspector', '=', True)])

    # Reschedule fields
    new_date = fields.Date(string='New Date')
    time_slot = fields.Selection([
        ('morning', 'Morning (8:00 - 12:00)'),
        ('afternoon', 'Afternoon (12:00 - 17:00)'),
        ('evening', 'Evening (17:00 - 20:00)'),
    ], string='Time Slot')

    # Notification options
    notify_inspectors = fields.Boolean(string='Notify Inspectors', default=True)
    notify_owners = fields.Boolean(string='Notify Property Owners', default=False)
    custom_message = fields.Text(string='Custom Message')

    # Cancel reason
    cancel_reason = fields.Text(string='Cancellation Reason')

    # Summary
    job_count = fields.Integer(string='Job Count', compute='_compute_job_count')

    @api.depends('job_ids')
    def _compute_job_count(self):
        for wizard in self:
            wizard.job_count = len(wizard.job_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['job_ids'] = [(6, 0, active_ids)]
        return res

    def action_execute(self):
        """Execute the selected bulk operation"""
        self.ensure_one()
        if not self.job_ids:
            raise UserError(_('No jobs selected!'))

        if self.operation == 'update_status':
            return self._action_update_status()
        elif self.operation == 'assign_inspector':
            return self._action_assign_inspector()
        elif self.operation == 'reschedule':
            return self._action_reschedule()
        elif self.operation == 'send_notifications':
            return self._action_send_notifications()
        elif self.operation == 'cancel':
            return self._action_cancel()

    def _action_update_status(self):
        """Update status for all selected jobs"""
        if not self.new_state:
            raise UserError(_('Please select a new status!'))

        updated = 0
        for job in self.job_ids:
            job.write({'state': self.new_state})
            updated += 1

        return self._show_result(_(f'{updated} jobs updated to {self.new_state}'))

    def _action_assign_inspector(self):
        """Assign inspector to all selected jobs"""
        if not self.inspector_id:
            raise UserError(_('Please select an inspector!'))

        updated = 0
        for job in self.job_ids:
            job.write({'inspector_id': self.inspector_id.id})
            updated += 1

        return self._show_result(_(f'{updated} jobs assigned to {self.inspector_id.name}'))

    def _action_reschedule(self):
        """Reschedule all selected jobs"""
        if not self.new_date:
            raise UserError(_('Please select a new date!'))

        updated = 0
        for job in self.job_ids:
            job.write({'scheduled_date': self.new_date})
            updated += 1

        return self._show_result(_(f'{updated} jobs rescheduled to {self.new_date}'))

    def _action_send_notifications(self):
        """Send notifications for selected jobs"""
        emails_sent = 0
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if self.notify_owners:
            template = self.env.ref('property_fielder_field_service.email_template_owner_appointment', raise_if_not_found=False)
            for job in self.job_ids:
                if job.partner_id and job.partner_id.email and template:
                    template.with_context(base_url=base_url, custom_message=self.custom_message).send_mail(job.id, force_send=True)
                    emails_sent += 1

        return self._show_result(_(f'{emails_sent} notifications sent'))

    def _action_cancel(self):
        """Cancel all selected jobs"""
        cancelled = 0
        for job in self.job_ids:
            job.write({'state': 'cancelled', 'notes': self.cancel_reason or job.notes})
            cancelled += 1

        return self._show_result(_(f'{cancelled} jobs cancelled'))

    def _show_result(self, message):
        """Show result notification"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Operation Complete'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

