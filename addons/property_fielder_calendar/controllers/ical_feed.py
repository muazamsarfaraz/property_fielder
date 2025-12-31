# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ICalFeedController(http.Controller):
    """Provide iCal feeds for calendar subscriptions"""
    
    @http.route('/calendar/ical/<string:token>.ics', type='http', auth='public', csrf=False)
    def ical_feed(self, token, **kwargs):
        """Generate iCal feed for inspector's jobs"""
        # Find inspector calendar by token
        inspector_calendar = request.env['property_fielder.inspector.calendar'].sudo().search([
            ('ical_token', '=', token)
        ], limit=1)
        
        if not inspector_calendar:
            return request.not_found()
        
        # Check if iCal is enabled
        config = request.env['property_fielder.calendar.config'].sudo().search([
            ('ical_enabled', '=', True),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            return request.not_found()
        
        inspector = inspector_calendar.inspector_id
        
        # Get jobs for the next 30 days
        today = datetime.now().date()
        end_date = today + timedelta(days=30)
        
        jobs = request.env['property_fielder.job'].sudo().search([
            ('inspector_id', '=', inspector.id),
            ('scheduled_date', '>=', today),
            ('scheduled_date', '<=', end_date),
            ('state', 'not in', ['cancelled']),
        ], order='scheduled_date, earliest_start')
        
        # Generate iCal content
        ical_content = self._generate_ical(inspector, jobs)
        
        return request.make_response(
            ical_content,
            headers=[
                ('Content-Type', 'text/calendar; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{inspector.name}_jobs.ics"'),
            ]
        )
    
    def _generate_ical(self, inspector, jobs):
        """Generate iCal format content"""
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Property Fielder//Job Calendar//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            f'X-WR-CALNAME:{inspector.name} - Jobs',
            'X-WR-TIMEZONE:Europe/London',
        ]
        
        for job in jobs:
            lines.extend(self._generate_vevent(job))
        
        lines.append('END:VCALENDAR')
        
        return '\r\n'.join(lines)
    
    def _generate_vevent(self, job):
        """Generate VEVENT for a job"""
        address = ', '.join(filter(None, [
            job.street, job.city, job.zip
        ]))
        
        # Format datetime for iCal
        def format_dt(dt):
            if dt:
                return dt.strftime('%Y%m%dT%H%M%SZ')
            return ''
        
        uid = f"job-{job.id}@propertyfielder.com"
        dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        description = f"Job Number: {job.job_number}\\nCustomer: {job.partner_id.name}\\nPriority: {job.priority}"
        if job.notes:
            description += f"\\n\\nNotes: {job.notes}"
        
        lines = [
            'BEGIN:VEVENT',
            f'UID:{uid}',
            f'DTSTAMP:{dtstamp}',
            f'DTSTART:{format_dt(job.earliest_start)}',
            f'DTEND:{format_dt(job.latest_end)}',
            f'SUMMARY:[{job.job_number}] {job.name}',
            f'DESCRIPTION:{description}',
            f'LOCATION:{address}',
        ]
        
        # Add status
        if job.state == 'completed':
            lines.append('STATUS:COMPLETED')
        elif job.state == 'in_progress':
            lines.append('STATUS:IN-PROCESS')
        else:
            lines.append('STATUS:CONFIRMED')
        
        # Add priority (1=high, 5=normal, 9=low for iCal)
        priority_map = {'urgent': '1', 'high': '2', 'normal': '5', 'low': '9'}
        lines.append(f'PRIORITY:{priority_map.get(job.priority, "5")}')
        
        lines.append('END:VEVENT')
        
        return lines

