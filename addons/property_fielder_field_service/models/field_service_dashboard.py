# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta


class FieldServiceDashboard(models.TransientModel):
    """Transient model for Field Service dashboard metrics and KPIs"""

    _name = 'property_fielder.field.service.dashboard'
    _description = 'Field Service Dashboard'

    name = fields.Char(string='Dashboard', default='Field Service Dashboard')
    
    # Today's Statistics
    today_jobs_total = fields.Integer(string='Jobs Today', compute='_compute_today_stats')
    today_jobs_pending = fields.Integer(string='Pending', compute='_compute_today_stats')
    today_jobs_in_progress = fields.Integer(string='In Progress', compute='_compute_today_stats')
    today_jobs_completed = fields.Integer(string='Completed', compute='_compute_today_stats')
    today_completion_rate = fields.Float(string='Completion %', compute='_compute_today_stats')
    
    # Inspector Statistics
    active_inspectors = fields.Integer(string='Active Inspectors', compute='_compute_inspector_stats')
    inspectors_on_job = fields.Integer(string='On Job', compute='_compute_inspector_stats')
    inspectors_available = fields.Integer(string='Available', compute='_compute_inspector_stats')
    inspector_utilization = fields.Float(string='Utilization %', compute='_compute_inspector_stats')
    total_capacity = fields.Integer(string='Total Capacity', compute='_compute_inspector_stats')
    jobs_assigned_today = fields.Integer(string='Jobs Assigned', compute='_compute_inspector_stats')
    
    # Route Statistics  
    today_routes = fields.Integer(string='Routes Today', compute='_compute_route_stats')
    routes_acknowledged = fields.Integer(string='Acknowledged', compute='_compute_route_stats')
    routes_pending = fields.Integer(string='Pending Ack', compute='_compute_route_stats')
    
    # Week Statistics
    week_jobs_total = fields.Integer(string='Jobs This Week', compute='_compute_week_stats')
    week_jobs_completed = fields.Integer(string='Completed This Week', compute='_compute_week_stats')
    week_avg_completion_time = fields.Float(string='Avg Completion (min)', compute='_compute_week_stats')
    
    # Confirmation Statistics
    pending_confirmations = fields.Integer(string='Pending Confirmations', compute='_compute_confirmation_stats')
    confirmed_today = fields.Integer(string='Confirmed Today', compute='_compute_confirmation_stats')
    declined_today = fields.Integer(string='Declined Today', compute='_compute_confirmation_stats')
    
    # Change Requests
    pending_change_requests = fields.Integer(string='Pending Changes', compute='_compute_change_stats')
    
    @api.depends_context('uid')
    def _compute_today_stats(self):
        Job = self.env['property_fielder.job']
        today = fields.Date.today()
        
        for rec in self:
            today_jobs = Job.search([('scheduled_date', '=', today)])
            rec.today_jobs_total = len(today_jobs)
            rec.today_jobs_pending = len(today_jobs.filtered(lambda j: j.state in ['draft', 'scheduled']))
            rec.today_jobs_in_progress = len(today_jobs.filtered(lambda j: j.state == 'in_progress'))
            rec.today_jobs_completed = len(today_jobs.filtered(lambda j: j.state == 'completed'))
            rec.today_completion_rate = (rec.today_jobs_completed / rec.today_jobs_total * 100) if rec.today_jobs_total else 0
    
    @api.depends_context('uid')
    def _compute_inspector_stats(self):
        Inspector = self.env['property_fielder.inspector']
        Job = self.env['property_fielder.job']
        today = fields.Date.today()

        for rec in self:
            inspectors = Inspector.search([('active', '=', True)])
            rec.active_inspectors = len(inspectors)

            # Inspectors with in-progress jobs
            inspectors_with_active = Job.search([
                ('scheduled_date', '=', today),
                ('state', '=', 'in_progress')
            ]).mapped('inspector_id')
            rec.inspectors_on_job = len(inspectors_with_active)
            rec.inspectors_available = rec.active_inspectors - rec.inspectors_on_job

            # Calculate capacity and utilization
            rec.total_capacity = sum(inspectors.mapped('max_jobs_per_day'))
            rec.jobs_assigned_today = Job.search_count([
                ('scheduled_date', '=', today),
                ('inspector_id', '!=', False)
            ])
            rec.inspector_utilization = (rec.jobs_assigned_today / rec.total_capacity * 100) if rec.total_capacity else 0
    
    @api.depends_context('uid')
    def _compute_route_stats(self):
        Route = self.env['property_fielder.route']
        today = fields.Date.today()
        
        for rec in self:
            today_routes = Route.search([('route_date', '=', today)])
            rec.today_routes = len(today_routes)
            rec.routes_acknowledged = len(today_routes.filtered(lambda r: r.inspector_acknowledged))
            rec.routes_pending = rec.today_routes - rec.routes_acknowledged
    
    @api.depends_context('uid')
    def _compute_week_stats(self):
        Job = self.env['property_fielder.job']
        today = fields.Date.today()
        week_start = today - timedelta(days=today.weekday())
        
        for rec in self:
            week_jobs = Job.search([
                ('scheduled_date', '>=', week_start),
                ('scheduled_date', '<=', today)
            ])
            rec.week_jobs_total = len(week_jobs)
            rec.week_jobs_completed = len(week_jobs.filtered(lambda j: j.state == 'completed'))
            rec.week_avg_completion_time = 0  # TODO: Calculate from check-in/out
    
    @api.depends_context('uid')
    def _compute_confirmation_stats(self):
        Job = self.env['property_fielder.job']
        today = fields.Date.today()
        today_start = fields.Datetime.to_datetime(today)
        today_end = fields.Datetime.to_datetime(today + timedelta(days=1))

        for rec in self:
            rec.pending_confirmations = Job.search_count([
                ('confirmation_state', '=', 'pending'),
                ('owner_notified', '=', True)
            ])
            rec.confirmed_today = Job.search_count([
                ('confirmation_state', '=', 'confirmed'),
                ('confirmation_date', '>=', today_start),
                ('confirmation_date', '<', today_end)
            ])
            rec.declined_today = Job.search_count([
                ('confirmation_state', '=', 'declined'),
                ('confirmation_date', '>=', today_start),
                ('confirmation_date', '<', today_end)
            ])
    
    @api.depends_context('uid')
    def _compute_change_stats(self):
        for rec in self:
            rec.pending_change_requests = self.env['property_fielder.change.request'].search_count([
                ('state', '=', 'pending')
            ])
    
    @api.model
    def get_dashboard_data(self):
        """Return dashboard data as dict for JS widget"""
        rec = self.create({})
        rec._compute_today_stats()
        rec._compute_inspector_stats()
        rec._compute_route_stats()
        rec._compute_week_stats()
        rec._compute_confirmation_stats()
        rec._compute_change_stats()
        
        return {
            'today': {
                'total': rec.today_jobs_total,
                'pending': rec.today_jobs_pending,
                'in_progress': rec.today_jobs_in_progress,
                'completed': rec.today_jobs_completed,
                'completion_rate': rec.today_completion_rate,
            },
            'inspectors': {
                'active': rec.active_inspectors,
                'on_job': rec.inspectors_on_job,
                'available': rec.inspectors_available,
                'utilization': rec.inspector_utilization,
                'total_capacity': rec.total_capacity,
                'jobs_assigned': rec.jobs_assigned_today,
            },
            'routes': {
                'total': rec.today_routes,
                'acknowledged': rec.routes_acknowledged,
                'pending': rec.routes_pending,
            },
            'week': {
                'total': rec.week_jobs_total,
                'completed': rec.week_jobs_completed,
            },
            'confirmations': {
                'pending': rec.pending_confirmations,
                'confirmed_today': rec.confirmed_today,
                'declined_today': rec.declined_today,
            },
            'change_requests': rec.pending_change_requests,
        }

