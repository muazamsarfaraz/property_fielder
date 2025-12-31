# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class JobCalendarEvent(models.Model):
    """Tracks synced calendar events for jobs"""
    
    _name = 'property_fielder.job.calendar.event'
    _description = 'Job Calendar Event'
    
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        required=True,
        ondelete='cascade'
    )
    
    inspector_calendar_id = fields.Many2one(
        'property_fielder.inspector.calendar',
        string='Inspector Calendar',
        required=True,
        ondelete='cascade'
    )
    
    external_event_id = fields.Char(
        string='External Event ID',
        required=True,
        help='Event ID in the external calendar'
    )
    
    provider = fields.Selection(
        related='inspector_calendar_id.provider',
        store=True
    )
    
    last_sync = fields.Datetime(string='Last Synced')
    sync_status = fields.Selection([
        ('synced', 'Synced'),
        ('pending', 'Pending Sync'),
        ('error', 'Sync Error'),
    ], default='synced')
    
    error_message = fields.Text(string='Error Message')
    
    _sql_constraints = [
        ('job_calendar_unique',
         'UNIQUE(job_id, inspector_calendar_id)',
         'Job can only have one event per calendar!')
    ]


class JobCalendar(models.Model):
    """Extend Job model with calendar sync capabilities"""
    
    _inherit = 'property_fielder.job'
    
    calendar_event_ids = fields.One2many(
        'property_fielder.job.calendar.event',
        'job_id',
        string='Calendar Events'
    )
    
    calendar_synced = fields.Boolean(
        string='Calendar Synced',
        compute='_compute_calendar_synced'
    )
    
    @api.depends('calendar_event_ids')
    def _compute_calendar_synced(self):
        for job in self:
            job.calendar_synced = bool(job.calendar_event_ids)
    
    def _sync_to_calendar(self, action='create'):
        """Sync job to connected calendars"""
        self.ensure_one()
        
        if not self.inspector_id:
            return
        
        # Get inspector's connected calendars
        calendars = self.env['property_fielder.inspector.calendar'].search([
            ('inspector_id', '=', self.inspector_id.id),
            ('connection_status', '=', 'connected'),
            ('sync_enabled', '=', True),
        ])
        
        for calendar in calendars:
            try:
                if action == 'create':
                    self._create_calendar_event(calendar)
                elif action == 'update':
                    self._update_calendar_event(calendar)
                elif action == 'delete':
                    self._delete_calendar_event(calendar)
            except Exception as e:
                _logger.error(f"Calendar sync error for job {self.id}: {e}")
                calendar.write({
                    'last_error': str(e),
                    'connection_status': 'error',
                })
    
    def _create_calendar_event(self, calendar):
        """Create event in external calendar"""
        event_data = self._prepare_calendar_event_data()
        
        if calendar.provider == 'google':
            external_id = self._create_google_event(calendar, event_data)
        else:
            external_id = self._create_microsoft_event(calendar, event_data)
        
        if external_id:
            self.env['property_fielder.job.calendar.event'].create({
                'job_id': self.id,
                'inspector_calendar_id': calendar.id,
                'external_event_id': external_id,
                'last_sync': fields.Datetime.now(),
            })
    
    def _prepare_calendar_event_data(self):
        """Prepare event data for external calendar"""
        address = ', '.join(filter(None, [
            self.street, self.city, self.zip
        ]))
        
        return {
            'summary': f"[Job] {self.name}",
            'description': f"""
Job Number: {self.job_number}
Customer: {self.partner_id.name}
Address: {address}
Priority: {self.priority}

Notes: {self.notes or 'None'}
            """.strip(),
            'location': address,
            'start': self.earliest_start,
            'end': self.latest_end,
        }
    
    def _create_google_event(self, calendar, event_data):
        """Create event via Google Calendar API"""
        # Placeholder - actual implementation would use google-api-python-client
        _logger.info(f"Would create Google event for job {self.id}")
        return f"google_event_{self.id}"
    
    def _create_microsoft_event(self, calendar, event_data):
        """Create event via Microsoft Graph API"""
        # Placeholder - actual implementation would use msgraph-sdk-python
        _logger.info(f"Would create Microsoft event for job {self.id}")
        return f"microsoft_event_{self.id}"
    
    def _update_calendar_event(self, calendar):
        """Update event in external calendar"""
        event = self.env['property_fielder.job.calendar.event'].search([
            ('job_id', '=', self.id),
            ('inspector_calendar_id', '=', calendar.id),
        ], limit=1)
        
        if event:
            event_data = self._prepare_calendar_event_data()
            # Would call API to update event
            event.write({'last_sync': fields.Datetime.now()})
    
    def _delete_calendar_event(self, calendar):
        """Delete event from external calendar"""
        event = self.env['property_fielder.job.calendar.event'].search([
            ('job_id', '=', self.id),
            ('inspector_calendar_id', '=', calendar.id),
        ], limit=1)
        
        if event:
            # Would call API to delete event
            event.unlink()

