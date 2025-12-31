# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CostAnalysis(models.TransientModel):
    """Cost analysis for inspections and routes"""
    
    _name = 'property_fielder.cost.analysis'
    _description = 'Cost Analysis'
    
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
    
    # Cost parameters
    hourly_rate = fields.Float(
        string='Hourly Rate (£)',
        default=25.0,
        help='Average hourly rate for inspectors'
    )
    mileage_rate = fields.Float(
        string='Mileage Rate (£/mile)',
        default=0.45,
        help='Mileage reimbursement rate'
    )
    
    # Summary stats
    total_jobs = fields.Integer(string='Total Jobs', compute='_compute_costs')
    total_routes = fields.Integer(string='Total Routes', compute='_compute_costs')
    total_hours = fields.Float(string='Total Hours', compute='_compute_costs')
    total_miles = fields.Float(string='Total Miles', compute='_compute_costs')
    
    # Costs
    labor_cost = fields.Float(string='Labor Cost (£)', compute='_compute_costs')
    mileage_cost = fields.Float(string='Mileage Cost (£)', compute='_compute_costs')
    total_cost = fields.Float(string='Total Cost (£)', compute='_compute_costs')
    cost_per_job = fields.Float(string='Cost per Job (£)', compute='_compute_costs')
    
    # Detail lines
    inspector_cost_ids = fields.One2many(
        'property_fielder.inspector.cost.line',
        'analysis_id',
        string='Cost by Inspector'
    )
    
    @api.depends('date_from', 'date_to', 'inspector_ids', 'hourly_rate', 'mileage_rate')
    def _compute_costs(self):
        for record in self:
            # Build domain
            domain = [
                ('scheduled_date', '>=', record.date_from),
                ('scheduled_date', '<=', record.date_to),
            ]
            if record.inspector_ids:
                domain.append(('inspector_id', 'in', record.inspector_ids.ids))
            
            jobs = self.env['property_fielder.job'].search(domain)
            routes = jobs.mapped('route_id')
            
            record.total_jobs = len(jobs)
            record.total_routes = len(routes)
            
            # Calculate total hours from job durations
            total_minutes = sum(j.duration_minutes for j in jobs)
            record.total_hours = round(total_minutes / 60, 1)
            
            # Calculate total miles from routes
            total_km = sum(r.total_distance for r in routes if r.total_distance)
            record.total_miles = round(total_km * 0.621371, 1)  # km to miles
            
            # Calculate costs
            record.labor_cost = round(record.total_hours * record.hourly_rate, 2)
            record.mileage_cost = round(record.total_miles * record.mileage_rate, 2)
            record.total_cost = record.labor_cost + record.mileage_cost
            record.cost_per_job = round(record.total_cost / record.total_jobs, 2) if record.total_jobs else 0
    
    def action_generate_breakdown(self):
        """Generate cost breakdown by inspector"""
        self.ensure_one()
        
        # Clear existing
        self.inspector_cost_ids.unlink()
        
        # Get inspectors
        if self.inspector_ids:
            inspectors = self.inspector_ids
        else:
            inspectors = self.env['property_fielder.inspector'].search([])
        
        lines = []
        for inspector in inspectors:
            # Get jobs for this inspector
            domain = [
                ('scheduled_date', '>=', self.date_from),
                ('scheduled_date', '<=', self.date_to),
                ('inspector_id', '=', inspector.id),
            ]
            jobs = self.env['property_fielder.job'].search(domain)
            
            if not jobs:
                continue
            
            routes = jobs.mapped('route_id')
            
            total_minutes = sum(j.duration_minutes for j in jobs)
            hours = total_minutes / 60
            
            total_km = sum(r.total_distance for r in routes if r.total_distance)
            miles = total_km * 0.621371
            
            labor = hours * self.hourly_rate
            mileage = miles * self.mileage_rate
            
            lines.append((0, 0, {
                'analysis_id': self.id,
                'inspector_id': inspector.id,
                'jobs_count': len(jobs),
                'routes_count': len(routes),
                'hours': round(hours, 1),
                'miles': round(miles, 1),
                'labor_cost': round(labor, 2),
                'mileage_cost': round(mileage, 2),
                'total_cost': round(labor + mileage, 2),
            }))
        
        self.inspector_cost_ids = lines
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cost Analysis'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }


class InspectorCostLine(models.TransientModel):
    _name = 'property_fielder.inspector.cost.line'
    _description = 'Inspector Cost Line'
    
    analysis_id = fields.Many2one('property_fielder.cost.analysis', ondelete='cascade')
    inspector_id = fields.Many2one('property_fielder.inspector', string='Inspector')
    jobs_count = fields.Integer(string='Jobs')
    routes_count = fields.Integer(string='Routes')
    hours = fields.Float(string='Hours')
    miles = fields.Float(string='Miles')
    labor_cost = fields.Float(string='Labor (£)')
    mileage_cost = fields.Float(string='Mileage (£)')
    total_cost = fields.Float(string='Total (£)')

