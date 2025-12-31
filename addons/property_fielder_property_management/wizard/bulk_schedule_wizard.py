# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta


class BulkScheduleWizard(models.TransientModel):
    """Wizard for bulk scheduling inspections from properties.
    
    Allows users to:
    1. Select properties with certifications expiring in next 14-30 days
    2. Choose certification types to schedule
    3. Create inspection jobs for all selected properties
    """
    _name = 'property_fielder.bulk.schedule.wizard'
    _description = 'Bulk Schedule Inspections Wizard'

    # Date range for finding properties with expiring certifications
    days_ahead_min = fields.Integer(
        string='Expiring in (min days)',
        default=0,
        help='Minimum days until certification expiry'
    )
    days_ahead_max = fields.Integer(
        string='Expiring in (max days)',
        default=30,
        help='Maximum days until certification expiry'
    )

    # Certification type filter
    certification_type_ids = fields.Many2many(
        'property_fielder.certification.type',
        'bulk_schedule_wiz_cert_type_rel',
        'wizard_id',
        'cert_type_id',
        string='Certification Types',
        help='Filter by certification types (leave empty for all)'
    )

    # Property selection
    property_ids = fields.Many2many(
        'property_fielder.property',
        'bulk_schedule_wiz_property_rel',
        'wizard_id',
        'property_id',
        string='Properties',
        help='Properties to schedule inspections for'
    )

    # Scheduling options
    scheduled_date = fields.Date(
        string='Scheduled Date',
        default=lambda self: date.today() + timedelta(days=7),
        help='Date to schedule inspections'
    )
    
    time_slot = fields.Selection([
        ('morning', 'Morning (8:00 - 12:00)'),
        ('afternoon', 'Afternoon (12:00 - 17:00)'),
        ('evening', 'Evening (17:00 - 20:00)'),
    ], string='Time Slot', default='morning')

    # Summary fields
    property_count = fields.Integer(
        string='Properties Selected',
        compute='_compute_counts'
    )
    certification_count = fields.Integer(
        string='Certifications Expiring',
        compute='_compute_counts'
    )

    @api.depends('property_ids')
    def _compute_counts(self):
        for wizard in self:
            wizard.property_count = len(wizard.property_ids)
            # Count expiring certifications for selected properties
            if wizard.property_ids:
                today = date.today()
                date_from = today + timedelta(days=wizard.days_ahead_min)
                date_to = today + timedelta(days=wizard.days_ahead_max)
                domain = [
                    ('property_id', 'in', wizard.property_ids.ids),
                    ('expiry_date', '>=', date_from),
                    ('expiry_date', '<=', date_to),
                    ('status', 'in', ['valid', 'expiring_soon']),
                ]
                if wizard.certification_type_ids:
                    domain.append(('certification_type_id', 'in', wizard.certification_type_ids.ids))
                wizard.certification_count = self.env['property_fielder.property.certification'].search_count(domain)
            else:
                wizard.certification_count = 0

    @api.model
    def default_get(self, fields_list):
        """Pre-fill properties if called from property list view"""
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'property_fielder.property' and \
           self.env.context.get('active_ids'):
            res['property_ids'] = [(6, 0, self.env.context.get('active_ids'))]
        return res

    def action_find_properties(self):
        """Find properties with certifications expiring in the date range"""
        self.ensure_one()
        
        today = date.today()
        date_from = today + timedelta(days=self.days_ahead_min)
        date_to = today + timedelta(days=self.days_ahead_max)

        # Find certifications expiring in range
        domain = [
            ('expiry_date', '>=', date_from),
            ('expiry_date', '<=', date_to),
            ('status', 'in', ['valid', 'expiring_soon']),
        ]
        if self.certification_type_ids:
            domain.append(('certification_type_id', 'in', self.certification_type_ids.ids))

        certs = self.env['property_fielder.property.certification'].search(domain)
        property_ids = certs.mapped('property_id').ids

        if not property_ids:
            raise UserError(_(
                'No properties found with certifications expiring between %s and %s days'
            ) % (self.days_ahead_min, self.days_ahead_max))

        self.property_ids = [(6, 0, property_ids)]

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_schedule_inspections(self):
        """Create inspection jobs for selected properties"""
        self.ensure_one()

        if not self.property_ids:
            raise UserError(_('Please select at least one property'))

        if not self.scheduled_date:
            raise UserError(_('Please select a scheduled date'))

        Job = self.env['property_fielder.job']
        created_jobs = self.env['property_fielder.job']
        skipped = []

        today = date.today()
        date_from = today + timedelta(days=self.days_ahead_min)
        date_to = today + timedelta(days=self.days_ahead_max)

        for prop in self.property_ids:
            # Find expiring certifications for this property
            domain = [
                ('property_id', '=', prop.id),
                ('expiry_date', '>=', date_from),
                ('expiry_date', '<=', date_to),
                ('status', 'in', ['valid', 'expiring_soon']),
            ]
            if self.certification_type_ids:
                domain.append(('certification_type_id', 'in', self.certification_type_ids.ids))

            certs = self.env['property_fielder.property.certification'].search(domain)

            if not certs:
                skipped.append(f'{prop.name} (no expiring certifications)')
                continue

            if not prop.partner_id:
                skipped.append(f'{prop.name} (no owner/customer)')
                continue

            # Create one job per certification type
            for cert in certs:
                job_vals = {
                    'name': f'{cert.certification_type_id.name} - {prop.name}',
                    'partner_id': prop.partner_id.id,
                    'property_id': prop.id,
                    'scheduled_date': self.scheduled_date,
                    'job_type': 'inspection',
                    'state': 'draft',
                    'street': prop.street,
                    'city': prop.city,
                    'postcode': prop.postcode,
                    'latitude': prop.latitude,
                    'longitude': prop.longitude,
                    'duration_minutes': cert.certification_type_id.default_duration_minutes or 60,
                    'notes': f'Certification renewal: {cert.certification_type_id.name}\n'
                             f'Current expiry: {cert.expiry_date}',
                }

                job = Job.create(job_vals)
                created_jobs |= job

        if not created_jobs:
            raise UserError(_('No jobs were created. Check the skipped properties.'))

        # Show result
        message = _('%d inspection jobs created for %d properties') % (
            len(created_jobs), len(self.property_ids) - len(skipped)
        )
        if skipped:
            message += _('\n\nSkipped:\n') + '\n'.join(f'- {s}' for s in skipped[:10])
            if len(skipped) > 10:
                message += f'\n... and {len(skipped) - 10} more'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Schedule Complete'),
                'message': message,
                'type': 'success',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': _('Created Jobs'),
                    'res_model': 'property_fielder.job',
                    'view_mode': 'list,form',
                    'domain': [('id', 'in', created_jobs.ids)],
                }
            }
        }

