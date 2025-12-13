# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


class CreateJobsWizard(models.TransientModel):
    _name = 'property_fielder.create.jobs.wizard'
    _description = 'Create Field Service Jobs from Inspections'

    # Date Range for filtering inspections
    date_from = fields.Date(
        string='Inspections Scheduled From',
        default=lambda self: date.today(),
        required=True,
        help='Show inspections scheduled from this date'
    )

    date_to = fields.Date(
        string='Inspections Scheduled To',
        default=lambda self: date.today() + timedelta(days=30),
        required=True,
        help='Show inspections scheduled until this date'
    )

    # Inspection selection
    inspection_ids = fields.Many2many(
        'property_fielder.property.inspection',
        'create_jobs_wiz_insp_rel',
        'wizard_id',
        'inspection_id',
        string='Inspections',
        help='Inspections to create jobs for'
    )

    inspection_count = fields.Integer(
        string='Inspection Count',
        compute='_compute_inspection_count'
    )

    # Job details
    duration_minutes = fields.Integer(
        string='Default Duration (minutes)',
        default=60,
        required=True,
        help='Default duration for each inspection job'
    )

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', required=True)

    notes = fields.Text(string='Additional Notes', help='Additional notes to add to all created jobs')

    @api.depends('inspection_ids')
    def _compute_inspection_count(self):
        for wizard in self:
            wizard.inspection_count = len(wizard.inspection_ids)

    @api.model
    def default_get(self, fields_list):
        """Pre-fill inspections based on context"""
        res = super().default_get(fields_list)

        # If called from inspection list view with selected inspections
        if self.env.context.get('active_model') == 'property_fielder.property.inspection' and \
           self.env.context.get('active_ids'):
            res['inspection_ids'] = [(6, 0, self.env.context.get('active_ids'))]

        return res

    def action_find_inspections(self):
        """Find inspections scheduled in the date range that don't have jobs"""
        self.ensure_one()

        # Find inspections in the date range without jobs
        inspections = self.env['property_fielder.property.inspection'].search([
            ('scheduled_date', '>=', self.date_from),
            ('scheduled_date', '<=', self.date_to),
            ('state', 'in', ['draft', 'scheduled']),
            ('job_id', '=', False)  # No job created yet
        ])

        if not inspections:
            raise UserError(_(
                'No inspections found without jobs between %s and %s'
            ) % (self.date_from, self.date_to))

        self.inspection_ids = [(6, 0, inspections.ids)]

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_jobs(self):
        """Create field service jobs for selected inspections"""
        self.ensure_one()

        if not self.inspection_ids:
            raise UserError(_('Please select at least one inspection'))

        Job = self.env['property_fielder.job']
        created_jobs = self.env['property_fielder.job']
        skipped_inspections = []

        for inspection in self.inspection_ids:
            # Skip inspections that already have jobs
            if inspection.job_id:
                skipped_inspections.append(f'{inspection.name} (already has job)')
                continue

            prop = inspection.property_id

            # Skip if property doesn't have a customer/partner
            if not prop.partner_id:
                skipped_inspections.append(f'{inspection.name} (property has no customer)')
                continue

            # Get default country (UK) if property doesn't have one
            country_id = prop.country_id.id if prop.country_id else self.env.ref('base.uk').id

            # Use inspection's scheduled_date for the job
            job_date = inspection.scheduled_date

            # Calculate earliest_start and latest_end based on scheduled_date
            # Default to 8 AM - 6 PM window
            earliest_start = datetime.combine(job_date, datetime.min.time()).replace(hour=8)
            latest_end = datetime.combine(job_date, datetime.min.time()).replace(hour=18)

            # Build job name from inspection details
            job_name = f'{inspection.certification_type_id.name}: {prop.name}'

            # Create job
            job_vals = {
                'name': job_name,
                'property_id': prop.id,
                'partner_id': prop.partner_id.id,
                'street': prop.street or 'Unknown',
                'city': prop.city or 'Unknown',
                'zip': prop.zip,
                'country_id': country_id,
                'latitude': prop.latitude or 0.0,
                'longitude': prop.longitude or 0.0,
                'scheduled_date': job_date,
                'earliest_start': earliest_start,
                'latest_end': latest_end,
                'duration_minutes': self.duration_minutes,
                'priority': self.priority,
                'inspector_id': inspection.inspector_id.id if inspection.inspector_id else False,
                'notes': f'Inspection: {inspection.name}\nType: {inspection.certification_type_id.name}\n{self.notes or ""}',
                'state': 'draft',
            }

            job = Job.create(job_vals)
            created_jobs |= job

            # Link job back to inspection
            inspection.write({
                'job_id': job.id,
                'state': 'scheduled' if inspection.state == 'draft' else inspection.state
            })

        # Show warning if inspections were skipped
        if skipped_inspections:
            message = _('The following inspections were skipped:\n\n%s') % '\n'.join(f'- {name}' for name in skipped_inspections)
            if created_jobs:
                # Some jobs were created, show info and continue
                pass
            else:
                raise UserError(message)

        if not created_jobs:
            raise UserError(_('No jobs were created. All selected inspections either already have jobs or have issues.'))

        # Show success message and open created jobs
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Jobs (%d)') % len(created_jobs),
            'res_model': 'property_fielder.job',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_jobs.ids)],
            'context': {'create': False},
        }

