# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FieldServiceJob(models.Model):
    """Jobs/Visits to be completed by inspectors"""
    
    _name = 'property_fielder.job'
    _description = 'Field Service Job'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, priority desc, id desc'
    
    # Basic Information
    name = fields.Char(
        string='Job Name',
        required=True,
        tracking=True,
        help='Name or description of the job'
    )
    
    job_number = fields.Char(
        string='Job Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique job identifier'
    )
    
    # Customer Information
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        help='Customer for this job'
    )

    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Phone',
        readonly=True
    )

    partner_email = fields.Char(
        related='partner_id.email',
        string='Email',
        readonly=True
    )
    
    # Location
    street = fields.Char(string='Street', required=True)
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City', required=True)
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        required=True,
        help='Latitude coordinate for routing'
    )
    
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        required=True,
        help='Longitude coordinate for routing'
    )
    
    # Scheduling
    scheduled_date = fields.Date(
        string='Scheduled Date',
        required=True,
        tracking=True,
        help='Date when job should be completed'
    )
    
    earliest_start = fields.Datetime(
        string='Earliest Start',
        required=True,
        tracking=True,
        help='Earliest time the job can start'
    )
    
    latest_end = fields.Datetime(
        string='Latest End',
        required=True,
        tracking=True,
        help='Latest time the job must be completed'
    )
    
    duration_minutes = fields.Integer(
        string='Duration (minutes)',
        required=True,
        default=60,
        help='Expected duration of the job in minutes'
    )

    # Scheduled time (set by optimizer)
    scheduled_arrival_time = fields.Datetime(
        string='Scheduled Arrival',
        readonly=True,
        tracking=True,
        help='Planned arrival time from route optimization'
    )

    scheduled_departure_time = fields.Datetime(
        string='Scheduled Departure',
        readonly=True,
        tracking=True,
        help='Planned departure time from route optimization'
    )

    # Skills & Priority
    skill_ids = fields.Many2many(
        'property_fielder.skill',
        'job_skill_rel',
        'job_id',
        'skill_id',
        string='Required Skills',
        help='Skills required to complete this job'
    )
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    
    # Assignment
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Assigned Inspector',
        tracking=True,
        help='Inspector assigned to this job'
    )
    
    route_id = fields.Many2one(
        'property_fielder.route',
        string='Route',
        readonly=True,
        help='Route this job is part of'
    )

    sequence_in_route = fields.Integer(
        string='Sequence in Route',
        default=0,
        help='Order of this job in the route'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Notes
    notes = fields.Text(string='Notes', help='Additional notes about the job')

    # ============================================================
    # APPOINTMENT CONFIRMATION FIELDS
    # ============================================================

    # Job Type
    job_type = fields.Selection([
        ('inspection', 'Inspection'),
        ('remediation', 'Remediation'),
        ('maintenance', 'Maintenance'),
        ('void_check', 'Void Check'),
        ('other', 'Other'),
    ], string='Job Type', default='inspection', tracking=True)

    # Confirmation Token (for email links)
    confirmation_token = fields.Char(
        string='Confirmation Token',
        copy=False,
        help='Secure token for confirmation links'
    )
    confirmation_token_expiry = fields.Datetime(
        string='Token Expiry',
        copy=False,
        help='When the confirmation token expires'
    )

    # Confirmation Status
    confirmation_state = fields.Selection([
        ('not_sent', 'Not Sent'),
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('rescheduled', 'Reschedule Requested'),
    ], string='Confirmation Status', default='not_sent', tracking=True)

    confirmation_date = fields.Datetime(
        string='Confirmation Date',
        readonly=True,
        help='When the appointment was confirmed/declined'
    )
    confirmation_method = fields.Selection([
        ('email_link', 'Email Link'),
        ('phone', 'Phone'),
        ('portal', 'Portal'),
        ('auto', 'Auto-confirmed'),
    ], string='Confirmation Method')

    # Reschedule Request
    proposed_reschedule_date = fields.Date(
        string='Proposed Reschedule Date',
        help='Date proposed by owner for rescheduling'
    )
    proposed_reschedule_time = fields.Char(
        string='Proposed Time Window',
        help='Time window proposed (e.g., "Morning", "14:00-16:00")'
    )
    reschedule_reason = fields.Text(
        string='Reschedule Reason',
        help='Reason given for reschedule/decline'
    )

    # Notification Tracking
    owner_notified = fields.Boolean(
        string='Owner Notified',
        default=False,
        help='Appointment notification sent to owner'
    )
    owner_notified_date = fields.Datetime(
        string='Notification Sent',
        readonly=True
    )
    reminder_sent = fields.Boolean(
        string='Reminder Sent',
        default=False,
        help='24-hour reminder sent'
    )
    reminder_sent_date = fields.Datetime(
        string='Reminder Sent Date',
        readonly=True
    )

    # HHSRS Integration - NOTE: These fields are now defined in property_fielder_hhsrs
    # which extends this model to add HHSRS-specific functionality
    is_hhsrs_remediation = fields.Boolean(
        string='HHSRS Remediation',
        default=False,
        help='Is this job for HHSRS hazard remediation'
    )
    # hhsrs_assessment_id and awaab_deadline_id are defined in property_fielder_hhsrs module
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate job number on create"""
        for vals in vals_list:
            if vals.get('job_number', _('New')) == _('New'):
                vals['job_number'] = self.env['ir.sequence'].next_by_code('property_fielder.job') or _('New')
        return super().create(vals_list)
    
    @api.constrains('earliest_start', 'latest_end')
    def _check_time_window(self):
        """Validate time window"""
        for job in self:
            if job.earliest_start >= job.latest_end:
                raise ValidationError(_('Earliest start must be before latest end!'))

    def action_request_change(self):
        """Open change request wizard for this job"""
        self.ensure_one()
        return {
            'name': _('Request Schedule Change'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.change.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_job_id': self.id,
                'default_requester_type': 'internal',
                'default_current_date': self.scheduled_date,
            },
        }

    # ============================================================
    # CONFIRMATION TOKEN METHODS
    # ============================================================

    def _generate_confirmation_token(self):
        """Generate a secure confirmation token for this job."""
        import secrets
        from datetime import timedelta

        self.ensure_one()
        token = secrets.token_urlsafe(32)
        expiry = fields.Datetime.now() + timedelta(hours=72)
        self.write({
            'confirmation_token': token,
            'confirmation_token_expiry': expiry,
            'confirmation_state': 'pending',
        })
        return token

    def _validate_confirmation_token(self, token):
        """Validate a confirmation token. Returns the job if valid, False otherwise."""
        if not token:
            return False
        job = self.sudo().search([
            ('confirmation_token', '=', token),
            ('confirmation_token_expiry', '>', fields.Datetime.now()),
        ], limit=1)
        return job if job else False

    def action_confirm_appointment(self, method='email_link'):
        """Confirm the appointment."""
        self.ensure_one()
        self.write({
            'confirmation_state': 'confirmed',
            'confirmation_date': fields.Datetime.now(),
            'confirmation_method': method,
            'confirmation_token': False,  # Clear token after use
            'confirmation_token_expiry': False,
        })
        self.message_post(
            body=_('Appointment confirmed by owner via %s') % method,
            message_type='notification'
        )

    def action_decline_appointment(self, reason=''):
        """Decline the appointment."""
        self.ensure_one()
        self.write({
            'confirmation_state': 'declined',
            'confirmation_date': fields.Datetime.now(),
            'reschedule_reason': reason,
            'confirmation_token': False,
            'confirmation_token_expiry': False,
        })
        # Create change request for dispatcher
        self.env['property_fielder.change.request'].create({
            'job_id': self.id,
            'request_type': 'cancel',
            'requester_type': 'owner',
            'requester_id': self.partner_id.id,
            'reason': reason or _('Owner declined appointment'),
            'state': 'pending',
        })
        self.message_post(
            body=_('Appointment declined by owner. Reason: %s') % (reason or 'Not specified'),
            message_type='notification'
        )

    def action_request_reschedule(self, proposed_date, proposed_time='', reason=''):
        """Request a reschedule."""
        self.ensure_one()
        self.write({
            'confirmation_state': 'rescheduled',
            'proposed_reschedule_date': proposed_date,
            'proposed_reschedule_time': proposed_time,
            'reschedule_reason': reason,
            'confirmation_token': False,
            'confirmation_token_expiry': False,
        })
        # Create change request for dispatcher
        self.env['property_fielder.change.request'].create({
            'job_id': self.id,
            'request_type': 'reschedule',
            'requester_type': 'owner',
            'requester_id': self.partner_id.id,
            'requested_date': proposed_date,
            'reason': reason or _('Owner requested reschedule to %s') % proposed_date,
            'state': 'pending',
        })
        self.message_post(
            body=_('Reschedule requested by owner to %s. Reason: %s') % (proposed_date, reason or 'Not specified'),
            message_type='notification'
        )

    def _apply_reschedule(self, new_date):
        """Apply a reschedule - update date and trigger re-optimization."""
        self.ensure_one()
        old_route = self.route_id
        self.write({
            'scheduled_date': new_date,
            'confirmation_state': 'pending',
            'route_id': False,  # Remove from current route
            'sequence_in_route': 0,
        })
        # Mark old route as needing re-optimization
        if old_route:
            old_route.write({
                'needs_reoptimization': True,
                'reoptimization_reason': _('Job %s rescheduled to %s') % (self.name, new_date),
            })
        self.message_post(
            body=_('Job rescheduled to %s. Removed from route.') % new_date,
            message_type='notification'
        )

    # ============================================================
    # CRON JOBS
    # ============================================================

    @api.model
    def _cron_send_appointment_reminders(self):
        """Send 24-hour appointment reminders for confirmed jobs."""
        from datetime import timedelta
        import logging
        _logger = logging.getLogger(__name__)

        tomorrow = fields.Date.today() + timedelta(days=1)

        # Find jobs scheduled for tomorrow that are confirmed but haven't received reminder
        jobs = self.search([
            ('scheduled_date', '=', tomorrow),
            ('confirmation_state', '=', 'confirmed'),
            ('reminder_sent', '=', False),
            ('owner_notified', '=', True),
            ('state', 'not in', ['completed', 'cancelled']),
        ])

        _logger.info(f'Sending appointment reminders for {len(jobs)} jobs')

        template = self.env.ref('property_fielder_field_service.email_template_appointment_reminder', raise_if_not_found=False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for job in jobs:
            try:
                if template and job.partner_id.email:
                    template.with_context(base_url=base_url).send_mail(job.id, force_send=True)
                    job.write({
                        'reminder_sent': True,
                        'reminder_sent_date': fields.Datetime.now(),
                    })
                    _logger.info(f'Reminder sent for job {job.name}')
            except Exception as e:
                _logger.error(f'Failed to send reminder for job {job.name}: {e}')

        return True

    @api.model
    def _cron_cleanup_expired_tokens(self):
        """Cleanup expired confirmation tokens."""
        import logging
        _logger = logging.getLogger(__name__)

        # Find jobs with expired tokens
        expired_jobs = self.search([
            ('confirmation_token', '!=', False),
            ('confirmation_token_expiry', '<', fields.Datetime.now()),
        ])

        if expired_jobs:
            _logger.info(f'Cleaning up {len(expired_jobs)} expired confirmation tokens')
            expired_jobs.write({
                'confirmation_token': False,
                'confirmation_token_expiry': False,
            })

        return True

    @api.model
    def action_create_test_data(self, count=20, scheduled_date=None):
        """Create test data for stress testing the dispatch view"""
        import random
        import logging
        from datetime import datetime, timedelta

        _logger = logging.getLogger(__name__)
        _logger.info(f"Creating test data: {count} properties for date {scheduled_date}")

        if not scheduled_date:
            scheduled_date = fields.Date.today()
        elif isinstance(scheduled_date, str):
            scheduled_date = fields.Date.from_string(scheduled_date)

        # Use Property model's cached reverse geocoding
        Property = self.env['property_fielder.property']

        try:
            # 1. Create test partner
            partner = self.env['res.partner'].create({
                'name': f'StressTest Customer {datetime.now().strftime("%Y%m%d%H%M%S")}',
                'is_company': True,
                'street': '1 Test Street',
                'city': 'London',
                'zip': 'SW1A 1AA',
            })

            # Get UK country
            uk_country = self.env.ref('base.uk', raise_if_not_found=False) or \
                         self.env['res.country'].search([('code', '=', 'GB')], limit=1)

            # Get a certification type
            cert_type = self.env['property_fielder.certification.type'].search([], limit=1)

            # 2. Create test inspectors if none exist
            Inspector = self.env['property_fielder.inspector']
            existing_inspectors = Inspector.search([])
            inspectors_created = 0

            if not existing_inspectors:
                # Create 3 test inspectors with London home locations
                inspector_data = [
                    {'name': 'John Smith', 'lat': 51.5074, 'lng': -0.1278},  # Central London
                    {'name': 'Sarah Jones', 'lat': 51.4934, 'lng': -0.1450},  # South Kensington
                    {'name': 'Mike Wilson', 'lat': 51.5290, 'lng': -0.0849},  # East London
                ]
                for insp in inspector_data:
                    # Find or create a user for this inspector
                    user = self.env['res.users'].search([('login', '=', insp['name'].lower().replace(' ', '.'))], limit=1)
                    if not user:
                        user = self.env['res.users'].with_context(no_reset_password=True).create({
                            'name': insp['name'],
                            'login': insp['name'].lower().replace(' ', '.'),
                            'password': 'test123',
                        })

                    Inspector.create({
                        'name': insp['name'],
                        'user_id': user.id,
                        'home_latitude': insp['lat'],
                        'home_longitude': insp['lng'],
                        'shift_start': 8.0,
                        'shift_end': 18.0,
                        'vehicle_capacity': 8,  # Max 8 jobs per inspector
                        'active': True,
                    })
                    inspectors_created += 1
                _logger.info(f"Created {inspectors_created} test inspectors")

            properties_created = 0
            inspections_created = 0
            jobs_created = 0

            # 3. Create properties with real geocoded addresses (using cached geocoding)
            for i in range(count):
                # Generate London coordinates with some variation
                base_lat, base_lng = 51.5074, -0.1278
                lat = base_lat + (random.random() - 0.5) * 0.15
                lng = base_lng + (random.random() - 0.5) * 0.25

                # Reverse geocode using Property model's cached method
                address = Property.reverse_geocode(lat, lng, use_cache=True)
                _logger.info(f"Property {i+1}: {address['street']}, {address['city']} ({lat:.4f}, {lng:.4f})")

                prop = self.env['property_fielder.property'].create({
                    'name': f'StressTest Property {i + 1}',
                    'partner_id': partner.id,
                    'street': address['street'],
                    'city': address['city'],
                    'zip': address['zip'],
                    'country_id': uk_country.id if uk_country else False,
                    'latitude': lat,
                    'longitude': lng,
                })
                properties_created += 1

                # 3. Create inspection for this property
                if cert_type:
                    inspection = self.env['property_fielder.property.inspection'].create({
                        'property_id': prop.id,
                        'certification_type_id': cert_type.id,
                        'scheduled_date': scheduled_date,
                        'state': 'draft',
                    })
                    inspections_created += 1

                    # 4. Create job from inspection
                    try:
                        inspection.action_create_field_service_job()
                        jobs_created += 1
                    except Exception as job_err:
                        _logger.error(f"Failed to create job for inspection {inspection.id}: {job_err}")

            _logger.info(f"Test data created: {properties_created} properties, {inspections_created} inspections, {jobs_created} jobs")
            return {
                'success': True,
                'properties': properties_created,
                'inspections': inspections_created,
                'jobs': jobs_created,
                'partner_id': partner.id,
            }

        except Exception as e:
            _logger.error(f"Error creating test data: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
            }

    @api.model
    def action_delete_test_data(self):
        """Delete all test data - routes, jobs, StressTest properties/partners"""
        try:
            # 1. Delete ALL routes first (they reference jobs/inspectors)
            routes = self.env['property_fielder.route'].search([])
            routes_deleted = len(routes)
            routes.unlink()

            # 2. Delete ALL jobs
            jobs = self.search([])
            jobs_deleted = len(jobs)
            jobs.unlink()

            # 3. Find StressTest properties
            properties = self.env['property_fielder.property'].search([
                ('name', 'ilike', 'StressTest')
            ])

            # 4. Find inspections for these properties
            inspections = self.env['property_fielder.property.inspection'].search([
                ('property_id', 'in', properties.ids)
            ])

            # 5. Find StressTest partners
            partners = self.env['res.partner'].search([
                ('name', 'ilike', 'StressTest')
            ])

            # Delete in correct order (inspections -> properties -> partners)
            inspections_deleted = len(inspections)
            inspections.unlink()

            properties_deleted = len(properties)
            properties.unlink()

            partners_deleted = len(partners)
            partners.unlink()

            return {
                'success': True,
                'routes': routes_deleted,
                'jobs': jobs_deleted,
                'inspections': inspections_deleted,
                'properties': properties_deleted,
                'partners': partners_deleted,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
