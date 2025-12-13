# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class JobCheckIn(models.Model):
    """Track inspector check-ins and check-outs for jobs"""
    
    _name = 'property_fielder.job.checkin'
    _description = 'Job Check-In/Out'
    _order = 'checkin_time desc'
    
    # Job Reference
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        required=True,
        ondelete='cascade',
        help='Job being checked into'
    )
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        help='Inspector performing the check-in'
    )
    
    # Check-in Details
    checkin_time = fields.Datetime(
        string='Check-In Time',
        required=True,
        default=fields.Datetime.now,
        help='When inspector arrived at job site'
    )
    
    checkin_latitude = fields.Float(
        string='Check-In Latitude',
        digits=(10, 7),
        help='GPS latitude at check-in'
    )
    
    checkin_longitude = fields.Float(
        string='Check-In Longitude',
        digits=(10, 7),
        help='GPS longitude at check-in'
    )
    
    checkin_accuracy = fields.Float(
        string='GPS Accuracy (meters)',
        help='GPS accuracy at check-in'
    )
    
    # Check-out Details
    checkout_time = fields.Datetime(
        string='Check-Out Time',
        help='When inspector left job site'
    )
    
    checkout_latitude = fields.Float(
        string='Check-Out Latitude',
        digits=(10, 7),
        help='GPS latitude at check-out'
    )
    
    checkout_longitude = fields.Float(
        string='Check-Out Longitude',
        digits=(10, 7),
        help='GPS longitude at check-out'
    )
    
    # Duration
    duration_minutes = fields.Integer(
        string='Duration (minutes)',
        compute='_compute_duration',
        store=True,
        help='Time spent on job'
    )
    
    # Status
    status = fields.Selection([
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out')
    ], string='Status', default='checked_in', required=True)
    
    # Notes
    checkin_notes = fields.Text(
        string='Check-In Notes',
        help='Notes at check-in'
    )
    
    checkout_notes = fields.Text(
        string='Check-Out Notes',
        help='Notes at check-out'
    )
    
    # Device Info
    device_info = fields.Char(
        string='Device Info',
        help='Mobile device information'
    )
    
    @api.depends('checkin_time', 'checkout_time')
    def _compute_duration(self):
        """Calculate duration between check-in and check-out"""
        for checkin in self:
            if checkin.checkin_time and checkin.checkout_time:
                delta = checkin.checkout_time - checkin.checkin_time
                checkin.duration_minutes = int(delta.total_seconds() / 60)
            else:
                checkin.duration_minutes = 0
    
    @api.constrains('checkin_time', 'checkout_time')
    def _check_times(self):
        """Validate check-in and check-out times"""
        for checkin in self:
            if checkin.checkout_time and checkin.checkin_time:
                if checkin.checkout_time <= checkin.checkin_time:
                    raise ValidationError(_('Check-out time must be after check-in time!'))
    
    def action_checkout(self, latitude=None, longitude=None, notes=None):
        """Check out from job"""
        self.ensure_one()
        
        if self.status == 'checked_out':
            raise ValidationError(_('Already checked out!'))
        
        self.write({
            'checkout_time': fields.Datetime.now(),
            'checkout_latitude': latitude,
            'checkout_longitude': longitude,
            'checkout_notes': notes,
            'status': 'checked_out'
        })
        
        # Update job status
        if self.job_id.state == 'in_progress':
            self.job_id.write({'state': 'completed'})
        
        return True

