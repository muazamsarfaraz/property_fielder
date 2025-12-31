# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class SafetyTimer(models.Model):
    """Lone Worker Safety Timer for HSE Compliance.
    
    Protects field inspectors working alone by:
    - Starting a timer when checking into a job
    - Allowing extensions if job takes longer
    - Auto-escalating if timer expires
    - Providing panic button for emergencies
    """
    
    _name = 'property_fielder.safety.timer'
    _description = 'Inspector Safety Timer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'started_at desc'
    
    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True
    )
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        ondelete='set null',
        tracking=True,
        help='Job associated with this safety timer'
    )
    
    # Timer timestamps
    started_at = fields.Datetime(
        string='Started At',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    
    expected_end = fields.Datetime(
        string='Expected End',
        required=True,
        tracking=True
    )
    
    actual_end = fields.Datetime(
        string='Actual End',
        tracking=True
    )
    
    # Extensions
    extended_count = fields.Integer(
        string='Extension Count',
        default=0,
        tracking=True
    )
    
    extension_minutes = fields.Integer(
        string='Total Extension (minutes)',
        default=0
    )
    
    # Location (for emergency response)
    last_known_lat = fields.Float(
        string='Last Known Latitude',
        digits=(10, 7)
    )
    
    last_known_long = fields.Float(
        string='Last Known Longitude',
        digits=(10, 7)
    )
    
    last_location_update = fields.Datetime(
        string='Last Location Update'
    )
    
    # State machine
    state = fields.Selection([
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('escalated', 'Escalated'),
        ('panic', 'Panic Triggered'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='active', required=True, tracking=True)
    
    # Escalation tracking
    overdue_at = fields.Datetime(
        string='Marked Overdue At'
    )
    
    escalated_at = fields.Datetime(
        string='Escalated At'
    )
    
    panic_triggered_at = fields.Datetime(
        string='Panic Triggered At'
    )
    
    # Notes
    notes = fields.Text(string='Notes')
    panic_reason = fields.Text(string='Panic Reason')
    
    # Computed
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue'
    )
    
    minutes_remaining = fields.Integer(
        string='Minutes Remaining',
        compute='_compute_minutes_remaining'
    )
    
    @api.depends('inspector_id', 'started_at')
    def _compute_name(self):
        for timer in self:
            if timer.inspector_id and timer.started_at:
                timer.name = f"SAFE/{timer.inspector_id.name}/{timer.started_at.strftime('%Y%m%d-%H%M')}"
            else:
                timer.name = _('New')
    
    @api.depends('expected_end', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for timer in self:
            timer.is_overdue = (
                timer.state == 'active' and 
                timer.expected_end and 
                timer.expected_end < now
            )
    
    @api.depends('expected_end', 'state')
    def _compute_minutes_remaining(self):
        now = fields.Datetime.now()
        for timer in self:
            if timer.state == 'active' and timer.expected_end:
                delta = timer.expected_end - now
                timer.minutes_remaining = int(delta.total_seconds() / 60)
            else:
                timer.minutes_remaining = 0
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def action_extend(self, minutes=30):
        """Extend the safety timer."""
        self.ensure_one()
        if self.state not in ('active', 'overdue'):
            raise UserError(_('Cannot extend a timer that is not active or overdue.'))
        
        self.write({
            'expected_end': self.expected_end + timedelta(minutes=minutes),
            'extended_count': self.extended_count + 1,
            'extension_minutes': self.extension_minutes + minutes,
            'state': 'active',  # Reset to active if was overdue
        })
        
        self.message_post(
            body=_('Timer extended by %d minutes. Total extensions: %d') % (
                minutes, self.extended_count
            ),
            message_type='notification'
        )
        
        return True
    
    def action_complete(self):
        """Mark timer as completed (inspector checked out safely)."""
        self.ensure_one()
        self.write({
            'state': 'completed',
            'actual_end': fields.Datetime.now(),
        })
        return True
    
    def action_cancel(self):
        """Cancel the safety timer."""
        self.ensure_one()
        self.write({
            'state': 'cancelled',
            'actual_end': fields.Datetime.now(),
        })
        return True

    def action_trigger_panic(self, reason=''):
        """Trigger panic button - immediate emergency response."""
        self.ensure_one()
        self.write({
            'state': 'panic',
            'panic_triggered_at': fields.Datetime.now(),
            'panic_reason': reason,
        })

        # Send immediate alerts
        self._send_panic_alert()

        self.message_post(
            body=_('🚨 PANIC BUTTON TRIGGERED! Reason: %s') % (reason or 'Not specified'),
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def _send_panic_alert(self):
        """Send immediate alerts to emergency contacts and managers."""
        self.ensure_one()

        # Get emergency contact from inspector
        inspector = self.inspector_id
        emergency_email = inspector.emergency_contact_email
        manager_email = inspector.user_id.partner_id.email if inspector.user_id else None

        # Build location link
        location_url = ''
        if self.last_known_lat and self.last_known_long:
            location_url = f'https://www.google.com/maps?q={self.last_known_lat},{self.last_known_long}'

        # Send email to manager group
        template = self.env.ref(
            'property_fielder_field_service_mobile.email_template_safety_panic',
            raise_if_not_found=False
        )
        if template:
            template.with_context(location_url=location_url).send_mail(self.id, force_send=True)
        else:
            # Fallback: post to chatter
            _logger.warning('Safety panic email template not found, using chatter')
            self.message_post(
                body=_(
                    '🚨 PANIC ALERT - Inspector %s needs immediate assistance!\n'
                    'Job: %s\n'
                    'Location: %s\n'
                    'Reason: %s'
                ) % (
                    inspector.name,
                    self.job_id.name if self.job_id else 'N/A',
                    location_url or 'Unknown',
                    self.panic_reason or 'Not specified'
                ),
                message_type='notification'
            )

    def _send_overdue_alert(self):
        """Send overdue alert to manager."""
        self.ensure_one()

        template = self.env.ref(
            'property_fielder_field_service_mobile.email_template_safety_overdue',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)
        else:
            _logger.warning('Safety overdue email template not found')

    def _escalate_to_manager(self):
        """Escalate overdue timer to manager."""
        self.ensure_one()
        self.write({
            'state': 'escalated',
            'escalated_at': fields.Datetime.now(),
        })

        template = self.env.ref(
            'property_fielder_field_service_mobile.email_template_safety_escalation',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)

        self.message_post(
            body=_('⚠️ Timer ESCALATED to manager after being overdue for 15+ minutes.'),
            message_type='notification'
        )

    def update_location(self, latitude, longitude):
        """Update last known location from mobile app."""
        self.ensure_one()
        self.write({
            'last_known_lat': latitude,
            'last_known_long': longitude,
            'last_location_update': fields.Datetime.now(),
        })
        return True

    # ============================================================
    # CRON JOB
    # ============================================================

    @api.model
    def _cron_check_overdue_timers(self):
        """Cron job: Runs every 5 minutes to check for overdue safety timers."""
        now = fields.Datetime.now()
        escalation_threshold = now - timedelta(minutes=15)

        # Find active timers that are overdue
        overdue_timers = self.search([
            ('state', '=', 'active'),
            ('expected_end', '<', now),
        ])

        for timer in overdue_timers:
            timer.write({
                'state': 'overdue',
                'overdue_at': now,
            })
            timer._send_overdue_alert()
            _logger.info(f'Safety timer {timer.name} marked as overdue')

        # Escalate timers that have been overdue for 15+ minutes
        escalation_timers = self.search([
            ('state', '=', 'overdue'),
            ('overdue_at', '<', escalation_threshold),
        ])

        for timer in escalation_timers:
            timer._escalate_to_manager()
            _logger.warning(f'Safety timer {timer.name} ESCALATED to manager')

        return True

    # ============================================================
    # HELPER METHODS
    # ============================================================

    @api.model
    def start_timer_for_job(self, job_id, duration_minutes=60, latitude=None, longitude=None):
        """Create and start a safety timer for a job."""
        job = self.env['property_fielder.job'].browse(job_id)
        if not job.exists():
            raise UserError(_('Job not found'))

        if not job.inspector_id:
            raise UserError(_('Job has no assigned inspector'))

        # Check for existing active timer for this inspector
        existing = self.search([
            ('inspector_id', '=', job.inspector_id.id),
            ('state', '=', 'active'),
        ], limit=1)

        if existing:
            # Complete existing timer first
            existing.action_complete()

        # Create new timer
        now = fields.Datetime.now()
        timer = self.create({
            'inspector_id': job.inspector_id.id,
            'job_id': job.id,
            'started_at': now,
            'expected_end': now + timedelta(minutes=duration_minutes),
            'last_known_lat': latitude,
            'last_known_long': longitude,
            'last_location_update': now if latitude else False,
        })

        return timer

    @api.model
    def get_active_timer_for_inspector(self, inspector_id):
        """Get the active safety timer for an inspector."""
        return self.search([
            ('inspector_id', '=', inspector_id),
            ('state', '=', 'active'),
        ], limit=1)

