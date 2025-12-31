# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class PropertyCertification(models.Model):
    _name = 'property_fielder.property.certification'
    _description = 'Property Certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date desc, issue_date desc'

    name = fields.Char(string='Certificate Number', required=True, tracking=True)
    
    # Property & Type
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    certification_type_id = fields.Many2one(
        'property_fielder.certification.type',
        string='Certification Type',
        required=True,
        tracking=True
    )
    
    flage_category = fields.Selection(
        related='certification_type_id.flage_category',
        string='FLAGE+ Category',
        store=True
    )
    
    # Dates
    issue_date = fields.Date(
        string='Issue Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    expiry_date = fields.Date(
        string='Expiry Date',
        required=True,
        tracking=True
    )
    
    next_inspection_date = fields.Date(
        string='Next Inspection Date',
        compute='_compute_next_inspection_date',
        store=True
    )
    
    days_until_expiry = fields.Integer(
        string='Days Until Expiry',
        compute='_compute_days_until_expiry',
        store=True
    )
    
    # Status
    status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', compute='_compute_status', store=True, tracking=True)
    
    # Inspector/Certifier
    inspector_id = fields.Many2one('res.partner', string='Inspector/Certifier', tracking=True)
    inspector_company = fields.Char(string='Inspector Company')
    inspector_license = fields.Char(string='Inspector License Number')
    
    # Certificate Details
    certificate_file = fields.Binary(string='Certificate File', attachment=True)
    certificate_filename = fields.Char(string='Certificate Filename')
    
    # Compliance
    is_compliant = fields.Boolean(
        string='Compliant',
        compute='_compute_is_compliant',
        store=True
    )
    
    compliance_notes = fields.Text(string='Compliance Notes')
    
    # Related Inspection
    inspection_id = fields.Many2one(
        'property_fielder.property.inspection',
        string='Related Inspection',
        ondelete='set null'
    )
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends('issue_date', 'certification_type_id.validity_period')
    def _compute_next_inspection_date(self):
        for cert in self:
            if cert.issue_date and cert.certification_type_id:
                cert.next_inspection_date = cert.issue_date + timedelta(
                    days=cert.certification_type_id.validity_period
                )
            else:
                cert.next_inspection_date = False

    @api.depends('expiry_date')
    def _compute_days_until_expiry(self):
        today = fields.Date.today()
        for cert in self:
            if cert.expiry_date:
                delta = cert.expiry_date - today
                cert.days_until_expiry = delta.days
            else:
                cert.days_until_expiry = 0

    @api.depends('expiry_date', 'certification_type_id.warning_period')
    def _compute_status(self):
        today = fields.Date.today()
        for cert in self:
            if not cert.expiry_date:
                cert.status = 'valid'
            elif cert.expiry_date < today:
                cert.status = 'expired'
            elif cert.certification_type_id and cert.expiry_date <= (
                today + timedelta(days=cert.certification_type_id.warning_period)
            ):
                cert.status = 'expiring_soon'
            else:
                cert.status = 'valid'

    @api.depends('status')
    def _compute_is_compliant(self):
        for cert in self:
            cert.is_compliant = cert.status in ['valid', 'expiring_soon']

    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for cert in self:
            if cert.issue_date and cert.expiry_date and cert.expiry_date <= cert.issue_date:
                raise ValidationError(_('Expiry date must be after issue date!'))

    @api.onchange('certification_type_id', 'issue_date')
    def _onchange_certification_type(self):
        if self.certification_type_id and self.issue_date:
            self.expiry_date = self.issue_date + timedelta(
                days=self.certification_type_id.validity_period
            )

    def action_renew(self):
        """Create a new certification based on this one"""
        self.ensure_one()
        new_cert = self.copy({
            'name': _('New'),
            'issue_date': fields.Date.today(),
            'expiry_date': fields.Date.today() + timedelta(
                days=self.certification_type_id.validity_period
            ),
            'certificate_file': False,
            'certificate_filename': False,
            'inspection_id': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.property.certification',
            'res_id': new_cert.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        self.write({'status': 'cancelled'})

    # ==================== Scheduled Actions (Cron) ====================

    @api.model
    def _cron_update_certification_status(self):
        """Daily cron job to update certification statuses.

        This method:
        1. Recomputes status for all certifications
        2. Triggers property FLAGE+ status recomputation
        3. Logs summary of status changes
        """
        _logger = __import__('logging').getLogger(__name__)
        _logger.info("Starting daily certification status update...")

        # Get all non-cancelled certifications
        certifications = self.search([('status', '!=', 'cancelled')])

        # Track changes
        newly_expired = self.env['property_fielder.property.certification']
        newly_expiring = self.env['property_fielder.property.certification']

        today = fields.Date.today()

        for cert in certifications:
            old_status = cert.status

            # Force recompute status
            cert._compute_status()
            cert._compute_days_until_expiry()

            # Track status transitions
            if old_status != 'expired' and cert.status == 'expired':
                newly_expired |= cert
            elif old_status == 'valid' and cert.status == 'expiring_soon':
                newly_expiring |= cert

        # Force recompute on affected properties
        affected_properties = (newly_expired | newly_expiring).mapped('property_id')
        if affected_properties:
            affected_properties._compute_flage_status()
            affected_properties._compute_compliance_status()

        _logger.info(
            f"Certification status update complete: "
            f"{len(newly_expired)} newly expired, "
            f"{len(newly_expiring)} newly expiring soon"
        )

        # Create activities for newly expiring certificates
        for cert in newly_expiring:
            cert.activity_schedule(
                'mail.mail_activity_data_warning',
                date_deadline=cert.expiry_date,
                summary=f'{cert.certification_type_id.name} expiring soon',
                note=f'Certificate {cert.name} for {cert.property_id.name} '
                     f'will expire on {cert.expiry_date}. Please schedule renewal.'
            )

        # Create activities for expired certificates
        for cert in newly_expired:
            cert.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'{cert.certification_type_id.name} has EXPIRED',
                note=f'URGENT: Certificate {cert.name} for {cert.property_id.name} '
                     f'expired on {cert.expiry_date}. Immediate renewal required.'
            )

        return True

    @api.model
    def _cron_send_expiry_reminders(self):
        """Daily cron job to send expiry reminder emails.

        Sends reminders for certificates expiring based on configurable thresholds
        per certification type (alert_days_urgent, alert_days_warning, alert_days_notice).
        Falls back to defaults of 7, 14, 30 days if not configured.
        """
        _logger = __import__('logging').getLogger(__name__)
        _logger.info("Sending certification expiry reminders...")

        today = fields.Date.today()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Get email template
        template = self.env.ref(
            'property_fielder_property_management.email_template_cert_expiring',
            raise_if_not_found=False
        )

        emails_sent = 0

        # Get all certification types with their configured alert thresholds
        cert_types = self.env['property_fielder.certification.type'].search([])

        for cert_type in cert_types:
            # Get configurable thresholds from certification type (with defaults)
            reminder_periods = [
                cert_type.alert_days_urgent or 7,
                cert_type.alert_days_warning or 14,
                cert_type.alert_days_notice or 30,
            ]
            # Remove duplicates and sort
            reminder_periods = sorted(set(reminder_periods))

            for days in reminder_periods:
                target_date = today + __import__('datetime').timedelta(days=days)

                certs_expiring = self.search([
                    ('certification_type_id', '=', cert_type.id),
                    ('status', 'in', ['valid', 'expiring_soon']),
                    ('expiry_date', '=', target_date)
                ])

                for cert in certs_expiring:
                    partner = cert.property_id.partner_id
                    if partner and partner.email:
                        # Send email notification
                        if template:
                            try:
                                template.with_context(base_url=base_url).send_mail(
                                    cert.id, force_send=True
                                )
                                emails_sent += 1
                            except Exception as e:
                                _logger.error(f"Failed to send email for cert {cert.name}: {e}")

                        # Create activity for property manager
                        cert.activity_schedule(
                            'mail.mail_activity_data_warning',
                            date_deadline=today,
                            summary=f'{days} day reminder: {cert.certification_type_id.name}',
                            note=f'Certificate {cert.name} for {cert.property_id.name} '
                                 f'expires in {days} days ({cert.expiry_date}).'
                        )

                if certs_expiring:
                    _logger.info(f"  {len(certs_expiring)} {cert_type.name} certificates expiring in {days} days")

        _logger.info(f"Sent {emails_sent} expiry reminder emails")
        return True

    @api.model
    def _cron_send_expired_alerts(self):
        """Daily cron job to send alerts for newly expired certificates."""
        _logger = __import__('logging').getLogger(__name__)
        _logger.info("Checking for newly expired certificates...")

        today = fields.Date.today()
        yesterday = today - __import__('datetime').timedelta(days=1)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Get email template
        template = self.env.ref(
            'property_fielder_property_management.email_template_cert_expired',
            raise_if_not_found=False
        )

        # Find certificates that expired yesterday (newly expired)
        newly_expired = self.search([
            ('expiry_date', '=', yesterday),
            ('status', '=', 'expired')
        ])

        emails_sent = 0
        for cert in newly_expired:
            partner = cert.property_id.partner_id
            if partner and partner.email and template:
                try:
                    template.with_context(base_url=base_url).send_mail(
                        cert.id, force_send=True
                    )
                    emails_sent += 1
                except Exception as e:
                    _logger.error(f"Failed to send expired alert for cert {cert.name}: {e}")

        _logger.info(f"Sent {emails_sent} expired certificate alerts")
        return True

