# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FieldServiceInspector(models.Model):
    """Inspectors/Technicians who complete jobs"""
    
    _name = 'property_fielder.inspector'
    _description = 'Field Service Inspector'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Basic Information
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='Inspector/Technician name'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        help='Link to HR employee record'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        help='Link to Odoo user for portal access'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help='Uncheck to archive the inspector'
    )
    
    # Contact Information
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    
    # Home Location (for route start/end)
    home_street = fields.Char(string='Home Street')
    home_city = fields.Char(string='Home City')
    home_state_id = fields.Many2one('res.country.state', string='Home State')
    home_zip = fields.Char(string='Home ZIP')
    
    home_latitude = fields.Float(
        string='Home Latitude',
        digits=(10, 7),
        help='Home location latitude for route planning'
    )
    
    home_longitude = fields.Float(
        string='Home Longitude',
        digits=(10, 7),
        help='Home location longitude for route planning'
    )
    
    # Skills
    skill_ids = fields.Many2many(
        'property_fielder.skill',
        'inspector_skill_rel',
        'inspector_id',
        'skill_id',
        string='Skills',
        help='Skills this inspector possesses'
    )
    
    # Availability
    shift_start = fields.Float(
        string='Shift Start',
        default=8.0,
        help='Shift start time (e.g., 8.0 = 8:00 AM)'
    )
    
    shift_end = fields.Float(
        string='Shift End',
        default=17.0,
        help='Shift end time (e.g., 17.0 = 5:00 PM)'
    )
    
    max_jobs_per_day = fields.Integer(
        string='Max Jobs Per Day',
        default=10,
        help='Maximum number of jobs this inspector can handle per day'
    )
    
    # Vehicle Information
    vehicle_name = fields.Char(string='Vehicle Name')
    vehicle_capacity = fields.Integer(
        string='Vehicle Capacity',
        default=100,
        help='Vehicle capacity for equipment/materials'
    )
    
    # Statistics
    job_count = fields.Integer(
        string='Total Jobs',
        compute='_compute_job_count',
        store=False
    )
    
    route_count = fields.Integer(
        string='Total Routes',
        compute='_compute_route_count',
        store=False
    )

    available = fields.Boolean(
        string='Available',
        compute='_compute_available',
        store=False,
        help='Whether inspector is currently available for scheduling'
    )

    # Relations
    job_ids = fields.One2many(
        'property_fielder.job',
        'inspector_id',
        string='Assigned Jobs'
    )
    
    route_ids = fields.One2many(
        'property_fielder.route',
        'inspector_id',
        string='Routes'
    )
    
    @api.depends('job_ids')
    def _compute_job_count(self):
        """Count assigned jobs"""
        for inspector in self:
            inspector.job_count = len(inspector.job_ids)
    
    @api.depends('route_ids')
    def _compute_route_count(self):
        """Count routes"""
        for inspector in self:
            inspector.route_count = len(inspector.route_ids)

    def _compute_available(self):
        """Determine if inspector is available for scheduling.
        Currently just checks if inspector is active.
        Could be extended to check shift times, vacation, etc.
        """
        for inspector in self:
            # For now, available = active. In future, check shift times, vacation calendar, etc.
            inspector.available = inspector.active

    def action_view_jobs(self):
        """Open jobs assigned to this inspector"""
        return {
            'name': _('Jobs'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.job',
            'view_mode': 'tree,form',
            'domain': [('inspector_id', '=', self.id)],
            'context': {'default_inspector_id': self.id}
        }
    
    def action_view_routes(self):
        """Open routes for this inspector"""
        return {
            'name': _('Routes'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.route',
            'view_mode': 'tree,form',
            'domain': [('inspector_id', '=', self.id)],
            'context': {'default_inspector_id': self.id}
        }

