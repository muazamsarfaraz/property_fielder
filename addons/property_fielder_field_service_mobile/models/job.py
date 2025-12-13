# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Job(models.Model):
    _inherit = 'property_fielder.job'
    
    # Mobile-specific fields
    mobile_checkin_time = fields.Datetime(string='Mobile Check-In Time', readonly=True)
    mobile_checkout_time = fields.Datetime(string='Mobile Check-Out Time', readonly=True)
    mobile_location_lat = fields.Float(string='Check-In Latitude', readonly=True)
    mobile_location_lng = fields.Float(string='Check-In Longitude', readonly=True)
    
    def action_mobile_checkin(self):
        """Mobile check-in action"""
        self.ensure_one()
        if self.state in ['in_progress', 'completed']:
            raise UserError(_('This job is already checked in or completed.'))
        
        # Create check-in record
        self.env['property_fielder.job.checkin'].create({
            'job_id': self.id,
            'inspector_id': self.inspector_id.id,
            'checkin_time': fields.Datetime.now(),
            'location_lat': self.env.context.get('location_lat', 0.0),
            'location_lng': self.env.context.get('location_lng', 0.0),
        })
        
        # Update job state
        self.write({
            'state': 'in_progress',
            'mobile_checkin_time': fields.Datetime.now(),
            'mobile_location_lat': self.env.context.get('location_lat', 0.0),
            'mobile_location_lng': self.env.context.get('location_lng', 0.0),
        })
        
        return True
    
    def action_mobile_checkout(self):
        """Mobile check-out action"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_('You must check in before checking out.'))

        # Update job state
        self.write({
            'state': 'completed',
            'mobile_checkout_time': fields.Datetime.now(),
        })

        return True

    def action_view_location_map(self):
        """Open location in map"""
        self.ensure_one()
        # This would typically open a map view or external map application
        # For now, return a simple action
        return {
            'type': 'ir.actions.act_url',
            'url': f'https://www.google.com/maps/search/?api=1&query={self.property_id.latitude},{self.property_id.longitude}',
            'target': 'new',
        }

    def action_capture_photo(self):
        """Capture photo action"""
        self.ensure_one()
        # This would typically open the camera interface
        # For now, return a form to create a photo record
        return {
            'type': 'ir.actions.act_window',
            'name': _('Capture Photo'),
            'res_model': 'property_fielder.job.photo',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_job_id': self.id,
                'default_inspector_id': self.inspector_id.id,
            },
        }

    def action_capture_signature(self):
        """Capture signature action"""
        self.ensure_one()
        # This would typically open the signature pad interface
        # For now, return a form to create a signature record
        return {
            'type': 'ir.actions.act_window',
            'name': _('Capture Signature'),
            'res_model': 'property_fielder.job.signature',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_job_id': self.id,
                'default_inspector_id': self.inspector_id.id,
            },
        }

