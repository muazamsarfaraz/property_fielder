# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ShareScheduleWizard(models.TransientModel):
    """Wizard to share route schedule with inspectors and property owners"""

    _name = 'property_fielder.share.schedule.wizard'
    _description = 'Share Schedule Wizard'

    # Route Selection
    route_ids = fields.Many2many(
        'property_fielder.route',
        'share_schedule_wiz_route_rel',
        'wizard_id',
        'route_id',
        string='Routes',
        required=True,
        help='Routes to share'
    )

    # Sharing Options
    share_with_inspectors = fields.Boolean(
        string='Share with Inspectors',
        default=True,
        help='Send schedule to assigned inspectors'
    )

    share_with_owners = fields.Boolean(
        string='Share with Property Owners',
        default=False,
        help='Send appointment notifications to property owners'
    )

    # Additional Recipients
    additional_emails = fields.Char(
        string='Additional Recipients',
        help='Comma-separated list of additional email addresses'
    )

    # Message Customization
    include_map_link = fields.Boolean(
        string='Include Map Link',
        default=True,
        help='Include a link to view route on map'
    )

    custom_message = fields.Text(
        string='Custom Message',
        help='Optional custom message to include in emails'
    )

    # Computed fields
    inspector_count = fields.Integer(
        string='Inspector Count',
        compute='_compute_counts'
    )

    owner_count = fields.Integer(
        string='Property Owner Count',
        compute='_compute_counts'
    )

    job_count = fields.Integer(
        string='Job Count',
        compute='_compute_counts'
    )

    @api.depends('route_ids')
    def _compute_counts(self):
        """Compute counts for display"""
        for wizard in self:
            inspectors = wizard.route_ids.mapped('inspector_id')
            jobs = wizard.route_ids.mapped('job_ids')
            owners = jobs.mapped('partner_id')

            wizard.inspector_count = len(inspectors)
            wizard.job_count = len(jobs)
            wizard.owner_count = len(owners)

    @api.model
    def default_get(self, fields_list):
        """Set defaults from context"""
        res = super().default_get(fields_list)

        # Get routes from context
        if self._context.get('active_model') == 'property_fielder.route':
            route_ids = self._context.get('active_ids', [])
            if route_ids:
                res['route_ids'] = [(6, 0, route_ids)]

        return res

    def action_send_schedule(self):
        """Send schedule emails to selected recipients"""
        self.ensure_one()

        if not self.share_with_inspectors and not self.share_with_owners and not self.additional_emails:
            raise UserError(_('Please select at least one sharing option or add additional recipients.'))

        emails_sent = 0

        # Send to inspectors
        if self.share_with_inspectors:
            emails_sent += self._send_to_inspectors()

        # Send to property owners
        if self.share_with_owners:
            emails_sent += self._send_to_owners()

        # Send to additional recipients
        if self.additional_emails:
            emails_sent += self._send_to_additional()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Schedule Shared'),
                'message': _('%d emails sent successfully!') % emails_sent,
                'type': 'success',
                'sticky': False,
            }
        }

    def _send_to_inspectors(self):
        """Send schedule to inspectors with acknowledgment token"""
        emails_sent = 0
        template = self.env.ref('property_fielder_field_service.email_template_inspector_schedule', raise_if_not_found=False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for route in self.route_ids:
            inspector = route.inspector_id
            if inspector and inspector.email:
                # Generate acknowledgment token for inspector
                route._generate_acknowledgment_token()

                if template:
                    template.with_context(
                        custom_message=self.custom_message,
                        base_url=base_url
                    ).send_mail(route.id, force_send=True)
                else:
                    self._send_simple_email(inspector.email, route, 'inspector')
                emails_sent += 1

        return emails_sent

    def _send_to_owners(self):
        """Send appointment notifications to property owners with confirmation tokens"""
        emails_sent = 0
        template = self.env.ref('property_fielder_field_service.email_template_owner_appointment', raise_if_not_found=False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for route in self.route_ids:
            for job in route.job_ids:
                partner = job.partner_id
                if partner and partner.email:
                    # Generate confirmation token for owner
                    job._generate_confirmation_token()

                    # Mark as notified
                    job.write({
                        'owner_notified': True,
                        'owner_notified_date': fields.Datetime.now(),
                    })

                    if template:
                        template.with_context(
                            custom_message=self.custom_message,
                            base_url=base_url
                        ).send_mail(job.id, force_send=True)
                    else:
                        self._send_simple_email(partner.email, job, 'owner')
                    emails_sent += 1

        return emails_sent

    def _send_to_additional(self):
        """Send to additional email addresses"""
        emails_sent = 0
        if not self.additional_emails:
            return 0

        # Parse email addresses
        email_list = [e.strip() for e in self.additional_emails.split(',') if e.strip()]

        for email in email_list:
            # Send summary email with all routes
            self._send_summary_email(email)
            emails_sent += 1

        return emails_sent

    def _send_simple_email(self, email, record, recipient_type):
        """Send a simple email without template"""
        mail_values = {
            'subject': _('Your Schedule for %s') % (record.route_date if hasattr(record, 'route_date') else record.scheduled_date),
            'email_to': email,
            'body_html': self._build_email_body(record, recipient_type),
            'auto_delete': True,
        }
        self.env['mail.mail'].sudo().create(mail_values).send()

    def _send_summary_email(self, email):
        """Send summary email with all routes"""
        body = '<h2>Route Schedule Summary</h2>'

        for route in self.route_ids:
            body += f'''
            <h3>{route.name} - {route.route_date}</h3>
            <p><strong>Inspector:</strong> {route.inspector_id.name}</p>
            <p><strong>Jobs:</strong> {len(route.job_ids)}</p>
            <ul>
            '''
            for job in route.job_ids.sorted('sequence_in_route'):
                body += f'<li>{job.name} - {job.street}, {job.city}</li>'
            body += '</ul>'

        if self.custom_message:
            body += f'<p><em>{self.custom_message}</em></p>'

        mail_values = {
            'subject': _('Route Schedule Summary'),
            'email_to': email,
            'body_html': body,
            'auto_delete': True,
        }
        self.env['mail.mail'].sudo().create(mail_values).send()

    def _build_email_body(self, record, recipient_type):
        """Build email body HTML"""
        if recipient_type == 'inspector':
            # Route schedule for inspector
            route = record
            body = f'''
            <h2>Your Route Schedule for {route.route_date}</h2>
            <p><strong>Route:</strong> {route.name}</p>
            <p><strong>Number of Jobs:</strong> {len(route.job_ids)}</p>
            <h3>Job Schedule:</h3>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
                <tr style="background-color: #f2f2f2;">
                    <th>#</th>
                    <th>Job</th>
                    <th>Address</th>
                    <th>Duration</th>
                </tr>
            '''
            for i, job in enumerate(route.job_ids.sorted('sequence_in_route'), 1):
                body += f'''
                <tr>
                    <td>{i}</td>
                    <td>{job.name}</td>
                    <td>{job.street}, {job.city}</td>
                    <td>{job.duration_minutes} min</td>
                </tr>
                '''
            body += '</table>'
        else:
            # Appointment notification for owner
            job = record
            body = f'''
            <h2>Inspection Appointment Scheduled</h2>
            <p>Dear {job.partner_id.name},</p>
            <p>We have scheduled an inspection at your property:</p>
            <p><strong>Property:</strong> {job.street}, {job.city}</p>
            <p><strong>Date:</strong> {job.scheduled_date}</p>
            <p><strong>Duration:</strong> Approximately {job.duration_minutes} minutes</p>
            <p>If you need to reschedule, please contact us.</p>
            '''

        if self.custom_message:
            body += f'<p><em>{self.custom_message}</em></p>'

        return body
