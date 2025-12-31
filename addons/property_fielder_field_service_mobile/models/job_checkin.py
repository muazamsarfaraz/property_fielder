# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import math


class JobCheckIn(models.Model):
    """Track inspector check-ins and check-outs for jobs"""

    _name = 'property_fielder.job.checkin'
    _description = 'Job Check-In/Out'
    _order = 'checkin_time desc'

    # Default geofence radius in meters
    DEFAULT_GEOFENCE_RADIUS = 100

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

    # Geofence validation
    distance_from_job = fields.Float(
        string='Distance from Job (m)',
        compute='_compute_distance_from_job',
        store=True,
        help='Distance in meters from job location at check-in'
    )

    geofence_valid = fields.Boolean(
        string='Within Geofence',
        compute='_compute_geofence_valid',
        store=True,
        help='Whether check-in was within acceptable distance of job location'
    )

    geofence_radius = fields.Float(
        string='Geofence Radius (m)',
        default=100,
        help='Maximum allowed distance from job location for valid check-in'
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

    checkout_distance_from_job = fields.Float(
        string='Checkout Distance (m)',
        compute='_compute_checkout_distance',
        store=True,
        help='Distance in meters from job location at check-out'
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
    
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        Returns distance in meters.
        """
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in meters
        r = 6371000
        return c * r

    @api.depends('checkin_latitude', 'checkin_longitude', 'job_id.latitude', 'job_id.longitude')
    def _compute_distance_from_job(self):
        """Calculate distance from job location at check-in"""
        for checkin in self:
            if checkin.checkin_latitude and checkin.checkin_longitude and checkin.job_id:
                checkin.distance_from_job = self._haversine_distance(
                    checkin.checkin_latitude,
                    checkin.checkin_longitude,
                    checkin.job_id.latitude,
                    checkin.job_id.longitude
                )
            else:
                checkin.distance_from_job = 0.0

    @api.depends('distance_from_job', 'geofence_radius')
    def _compute_geofence_valid(self):
        """Check if check-in is within geofence"""
        for checkin in self:
            radius = checkin.geofence_radius or self.DEFAULT_GEOFENCE_RADIUS
            checkin.geofence_valid = checkin.distance_from_job <= radius

    @api.depends('checkout_latitude', 'checkout_longitude', 'job_id.latitude', 'job_id.longitude')
    def _compute_checkout_distance(self):
        """Calculate distance from job location at check-out"""
        for checkin in self:
            if checkin.checkout_latitude and checkin.checkout_longitude and checkin.job_id:
                checkin.checkout_distance_from_job = self._haversine_distance(
                    checkin.checkout_latitude,
                    checkin.checkout_longitude,
                    checkin.job_id.latitude,
                    checkin.job_id.longitude
                )
            else:
                checkin.checkout_distance_from_job = 0.0

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

    def get_location_info(self):
        """Get formatted location information for display"""
        self.ensure_one()
        return {
            'checkin': {
                'latitude': self.checkin_latitude,
                'longitude': self.checkin_longitude,
                'accuracy': self.checkin_accuracy,
                'distance_from_job': self.distance_from_job,
                'within_geofence': self.geofence_valid,
            },
            'checkout': {
                'latitude': self.checkout_latitude,
                'longitude': self.checkout_longitude,
                'distance_from_job': self.checkout_distance_from_job,
            } if self.checkout_time else None,
            'job': {
                'latitude': self.job_id.latitude,
                'longitude': self.job_id.longitude,
                'address': f"{self.job_id.street}, {self.job_id.city}",
            }
        }

