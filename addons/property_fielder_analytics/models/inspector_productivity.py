# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class InspectorProductivityReport(models.Model):
    """Inspector productivity analytics and reporting"""
    
    _name = 'property_fielder.inspector.productivity'
    _description = 'Inspector Productivity Report'
    _auto = False  # Database view, not a table
    _order = 'inspector_id, date desc'
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        readonly=True
    )
    inspector_name = fields.Char(string='Inspector Name', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    
    # Job Metrics
    jobs_assigned = fields.Integer(string='Jobs Assigned', readonly=True)
    jobs_completed = fields.Integer(string='Jobs Completed', readonly=True)
    jobs_cancelled = fields.Integer(string='Jobs Cancelled', readonly=True)
    completion_rate = fields.Float(string='Completion Rate (%)', readonly=True)
    
    # Time Metrics
    total_duration_minutes = fields.Integer(string='Total Job Duration (min)', readonly=True)
    avg_duration_minutes = fields.Float(string='Avg Job Duration (min)', readonly=True)
    total_travel_minutes = fields.Integer(string='Total Travel Time (min)', readonly=True)
    
    # Performance
    on_time_count = fields.Integer(string='On-Time Jobs', readonly=True)
    late_count = fields.Integer(string='Late Jobs', readonly=True)
    on_time_rate = fields.Float(string='On-Time Rate (%)', readonly=True)
    
    # Route Metrics
    route_count = fields.Integer(string='Routes', readonly=True)
    total_distance_km = fields.Float(string='Total Distance (km)', readonly=True)
    
    def init(self):
        """Create the database view for productivity analytics"""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS property_fielder_inspector_productivity;
            CREATE OR REPLACE VIEW property_fielder_inspector_productivity AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    i.id AS inspector_id,
                    i.name AS inspector_name,
                    j.scheduled_date AS date,
                    COUNT(j.id) AS jobs_assigned,
                    SUM(CASE WHEN j.state = 'completed' THEN 1 ELSE 0 END) AS jobs_completed,
                    SUM(CASE WHEN j.state = 'cancelled' THEN 1 ELSE 0 END) AS jobs_cancelled,
                    CASE 
                        WHEN COUNT(j.id) > 0 
                        THEN ROUND(100.0 * SUM(CASE WHEN j.state = 'completed' THEN 1 ELSE 0 END) / COUNT(j.id), 1)
                        ELSE 0 
                    END AS completion_rate,
                    SUM(j.duration_minutes) AS total_duration_minutes,
                    AVG(j.duration_minutes) AS avg_duration_minutes,
                    0 AS total_travel_minutes,
                    SUM(CASE WHEN j.state = 'completed' AND j.completed_date <= j.scheduled_date THEN 1 ELSE 0 END) AS on_time_count,
                    SUM(CASE WHEN j.state = 'completed' AND j.completed_date > j.scheduled_date THEN 1 ELSE 0 END) AS late_count,
                    CASE 
                        WHEN SUM(CASE WHEN j.state = 'completed' THEN 1 ELSE 0 END) > 0 
                        THEN ROUND(100.0 * SUM(CASE WHEN j.state = 'completed' AND j.completed_date <= j.scheduled_date THEN 1 ELSE 0 END) / 
                             NULLIF(SUM(CASE WHEN j.state = 'completed' THEN 1 ELSE 0 END), 0), 1)
                        ELSE 0 
                    END AS on_time_rate,
                    COUNT(DISTINCT j.route_id) AS route_count,
                    0.0 AS total_distance_km
                FROM property_fielder_inspector i
                LEFT JOIN property_fielder_job j ON j.inspector_id = i.id
                WHERE j.scheduled_date IS NOT NULL
                GROUP BY i.id, i.name, j.scheduled_date
            )
        """)


class InspectorProductivitySummary(models.TransientModel):
    """Summary view for inspector productivity - with date range filtering"""
    
    _name = 'property_fielder.inspector.productivity.summary'
    _description = 'Inspector Productivity Summary'
    
    # Filters
    date_from = fields.Date(
        string='From Date',
        default=lambda self: fields.Date.today() - timedelta(days=30)
    )
    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today
    )
    inspector_ids = fields.Many2many(
        'property_fielder.inspector',
        string='Inspectors',
        help='Leave empty for all inspectors'
    )
    
    # Summary results
    line_ids = fields.One2many(
        'property_fielder.inspector.productivity.line',
        'summary_id',
        string='Productivity Lines'
    )
    
    def action_generate_report(self):
        """Generate productivity report for selected period"""
        self.ensure_one()
        
        # Clear existing lines
        self.line_ids.unlink()
        
        # Build domain
        domain = [
            ('scheduled_date', '>=', self.date_from),
            ('scheduled_date', '<=', self.date_to),
        ]
        if self.inspector_ids:
            domain.append(('inspector_id', 'in', self.inspector_ids.ids))
        
        # Get all inspectors
        if self.inspector_ids:
            inspectors = self.inspector_ids
        else:
            inspectors = self.env['property_fielder.inspector'].search([])
        
        # Calculate metrics for each inspector
        Job = self.env['property_fielder.job']
        lines = []
        
        for inspector in inspectors:
            inspector_domain = domain + [('inspector_id', '=', inspector.id)]
            jobs = Job.search(inspector_domain)
            
            if not jobs:
                continue
            
            completed = jobs.filtered(lambda j: j.state == 'completed')
            cancelled = jobs.filtered(lambda j: j.state == 'cancelled')
            
            lines.append((0, 0, {
                'summary_id': self.id,
                'inspector_id': inspector.id,
                'jobs_assigned': len(jobs),
                'jobs_completed': len(completed),
                'jobs_cancelled': len(cancelled),
                'completion_rate': (len(completed) / len(jobs) * 100) if jobs else 0,
                'total_duration': sum(j.duration_minutes for j in jobs),
                'avg_duration': sum(j.duration_minutes for j in jobs) / len(jobs) if jobs else 0,
            }))
        
        self.line_ids = lines
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Productivity Report'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }


class InspectorProductivityLine(models.TransientModel):
    """Individual line in productivity summary"""
    
    _name = 'property_fielder.inspector.productivity.line'
    _description = 'Inspector Productivity Line'
    
    summary_id = fields.Many2one(
        'property_fielder.inspector.productivity.summary',
        string='Summary',
        ondelete='cascade'
    )
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector'
    )
    jobs_assigned = fields.Integer(string='Jobs Assigned')
    jobs_completed = fields.Integer(string='Completed')
    jobs_cancelled = fields.Integer(string='Cancelled')
    completion_rate = fields.Float(string='Completion %')
    total_duration = fields.Integer(string='Total Duration (min)')
    avg_duration = fields.Float(string='Avg Duration (min)')

