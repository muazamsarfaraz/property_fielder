# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FieldServiceRoute(models.Model):
    """Optimized routes for inspectors"""
    
    _name = 'property_fielder.route'
    _description = 'Field Service Route'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'route_date desc, id desc'
    
    # Basic Information
    name = fields.Char(
        string='Route Name',
        required=True,
        tracking=True,
        help='Name of the route'
    )
    
    route_number = fields.Char(
        string='Route Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique route identifier'
    )
    
    # Assignment
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        tracking=True,
        help='Inspector assigned to this route'
    )
    
    route_date = fields.Date(
        string='Route Date',
        required=True,
        tracking=True,
        help='Date for this route'
    )

    start_time = fields.Datetime(
        string='Start Time',
        help='Planned start time for the route'
    )

    # Jobs
    job_ids = fields.One2many(
        'property_fielder.job',
        'route_id',
        string='Jobs',
        help='Jobs in this route'
    )
    
    job_count = fields.Integer(
        string='Number of Jobs',
        compute='_compute_job_count',
        store=True
    )
    
    # Route Metrics
    total_distance_km = fields.Float(
        string='Total Distance (km)',
        digits=(10, 2),
        help='Total driving distance in kilometers'
    )
    
    total_drive_time_minutes = fields.Integer(
        string='Total Drive Time (min)',
        help='Total driving time in minutes'
    )
    
    total_work_time_minutes = fields.Integer(
        string='Total Work Time (min)',
        help='Total time spent on jobs'
    )
    
    total_time_minutes = fields.Integer(
        string='Total Time (min)',
        compute='_compute_total_time',
        store=True,
        help='Total route time (drive + work)'
    )
    
    # Optimization
    optimization_id = fields.Many2one(
        'property_fielder.optimization',
        string='Optimization Run',
        readonly=True,
        help='Optimization run that created this route'
    )
    
    optimization_score = fields.Char(
        string='Optimization Score',
        help='Score from Timefold Solver'
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('optimized', 'Optimized'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    # Route Geometry (for map display)
    route_geometry = fields.Text(
        string='Route Geometry',
        help='GeoJSON geometry for route visualization'
    )

    # ============================================================
    # RE-OPTIMIZATION & INSPECTOR ACKNOWLEDGMENT
    # ============================================================

    needs_reoptimization = fields.Boolean(
        string='Needs Re-optimization',
        default=False,
        tracking=True,
        help='Route needs re-optimization due to schedule changes'
    )
    reoptimization_reason = fields.Char(
        string='Re-optimization Reason',
        help='Why re-optimization is needed'
    )

    # Inspector Acknowledgment
    inspector_acknowledged = fields.Boolean(
        string='Inspector Acknowledged',
        default=False,
        help='Inspector has acknowledged receipt of schedule'
    )
    inspector_acknowledged_date = fields.Datetime(
        string='Acknowledged Date',
        readonly=True
    )
    inspector_acknowledgment_token = fields.Char(
        string='Acknowledgment Token',
        copy=False
    )

    # Confirmation Stats (computed)
    confirmed_job_count = fields.Integer(
        string='Confirmed Jobs',
        compute='_compute_confirmation_stats',
        store=True
    )
    pending_confirmation_count = fields.Integer(
        string='Pending Confirmations',
        compute='_compute_confirmation_stats',
        store=True
    )
    declined_job_count = fields.Integer(
        string='Declined Jobs',
        compute='_compute_confirmation_stats',
        store=True
    )

    @api.depends('job_ids.confirmation_state')
    def _compute_confirmation_stats(self):
        """Compute confirmation statistics for route jobs."""
        for route in self:
            jobs = route.job_ids
            route.confirmed_job_count = len(jobs.filtered(lambda j: j.confirmation_state == 'confirmed'))
            route.pending_confirmation_count = len(jobs.filtered(lambda j: j.confirmation_state == 'pending'))
            route.declined_job_count = len(jobs.filtered(lambda j: j.confirmation_state in ['declined', 'rescheduled']))
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate route number on create"""
        for vals in vals_list:
            if vals.get('route_number', _('New')) == _('New'):
                vals['route_number'] = self.env['ir.sequence'].next_by_code('property_fielder.route') or _('New')
        return super().create(vals_list)
    
    @api.depends('job_ids')
    def _compute_job_count(self):
        """Count jobs in route"""
        for route in self:
            route.job_count = len(route.job_ids)
    
    @api.depends('total_drive_time_minutes', 'total_work_time_minutes')
    def _compute_total_time(self):
        """Calculate total route time"""
        for route in self:
            route.total_time_minutes = route.total_drive_time_minutes + route.total_work_time_minutes
    
    def action_view_jobs(self):
        """Open jobs in this route"""
        return {
            'name': _('Route Jobs'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.job',
            'view_mode': 'tree,form',
            'domain': [('route_id', '=', self.id)],
            'context': {'default_route_id': self.id}
        }
    
    def action_view_map(self):
        """Open route on map"""
        return {
            'name': _('Route Map'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.route',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_share_schedule(self):
        """Open share schedule wizard"""
        return {
            'name': _('Share Schedule'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.share.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'property_fielder.route',
                'active_ids': self.ids,
                'default_route_ids': [(6, 0, self.ids)],
            },
        }

    # ============================================================
    # INSPECTOR ACKNOWLEDGMENT METHODS
    # ============================================================

    def _generate_acknowledgment_token(self):
        """Generate a secure token for inspector acknowledgment."""
        import secrets
        self.ensure_one()
        token = secrets.token_urlsafe(32)
        self.write({'inspector_acknowledgment_token': token})
        return token

    def action_acknowledge_schedule(self):
        """Inspector acknowledges receipt of schedule."""
        self.ensure_one()
        self.write({
            'inspector_acknowledged': True,
            'inspector_acknowledged_date': fields.Datetime.now(),
            'inspector_acknowledgment_token': False,
        })
        self.message_post(
            body=_('Schedule acknowledged by inspector %s') % self.inspector_id.name,
            message_type='notification'
        )

    def action_reoptimize(self):
        """Trigger re-optimization for this route."""
        self.ensure_one()
        # Get all jobs from this route
        jobs = self.job_ids
        if not jobs:
            return

        # Create new optimization run
        optimization = self.env['property_fielder.optimization'].create({
            'name': _('Re-optimization: %s') % self.name,
            'optimization_date': self.route_date,
            'job_ids': [(6, 0, jobs.ids)],
            'inspector_ids': [(6, 0, [self.inspector_id.id])],
            'state': 'draft',
        })

        # Clear re-optimization flag
        self.write({
            'needs_reoptimization': False,
            'reoptimization_reason': False,
        })

        # Run optimization
        optimization.action_run_optimization()

        return {
            'name': _('Re-optimization'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.optimization',
            'view_mode': 'form',
            'res_id': optimization.id,
        }

    def action_clear_reoptimization_flag(self):
        """Clear the re-optimization flag without re-optimizing."""
        self.write({
            'needs_reoptimization': False,
            'reoptimization_reason': False,
        })
