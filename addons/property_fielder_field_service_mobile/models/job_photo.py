# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobPhoto(models.Model):
    """Photos captured during job execution"""
    
    _name = 'property_fielder.job.photo'
    _description = 'Job Photo'
    _order = 'capture_time desc'
    
    # Job Reference
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        required=True,
        ondelete='cascade',
        help='Job this photo belongs to'
    )
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        help='Inspector who took the photo'
    )
    
    # Photo Details
    name = fields.Char(
        string='Photo Name',
        required=True,
        default='Photo',
        help='Description of the photo'
    )
    
    image = fields.Binary(
        string='Image',
        required=True,
        attachment=True,
        help='Photo image data'
    )
    
    image_filename = fields.Char(
        string='Filename',
        help='Original filename'
    )
    
    # Metadata
    capture_time = fields.Datetime(
        string='Capture Time',
        required=True,
        default=fields.Datetime.now,
        help='When photo was taken'
    )
    
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS latitude where photo was taken'
    )
    
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS longitude where photo was taken'
    )
    
    # Categories
    category = fields.Selection([
        ('before', 'Before'),
        ('during', 'During Work'),
        ('after', 'After'),
        ('issue', 'Issue/Problem'),
        ('damage', 'Damage'),
        ('completion', 'Completion'),
        ('other', 'Other')
    ], string='Category', default='during', required=True)
    
    # Notes
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the photo'
    )
    
    # Tags
    tag_ids = fields.Many2many(
        'property_fielder.photo.tag',
        string='Tags',
        help='Tags for categorizing photos'
    )
    
    # Device Info
    device_info = fields.Char(
        string='Device Info',
        help='Camera/device information'
    )
    
    # Thumbnail
    image_small = fields.Binary(
        string='Thumbnail',
        compute='_compute_thumbnail',
        store=True,
        attachment=True
    )
    
    @api.depends('image')
    def _compute_thumbnail(self):
        """Generate thumbnail from image"""
        for photo in self:
            if photo.image:
                # In a real implementation, resize the image
                # For now, just use the same image
                photo.image_small = photo.image
            else:
                photo.image_small = False


class PhotoTag(models.Model):
    """Tags for categorizing photos"""
    
    _name = 'property_fielder.photo.tag'
    _description = 'Photo Tag'
    
    name = fields.Char(
        string='Tag Name',
        required=True,
        help='Tag name'
    )
    
    color = fields.Integer(
        string='Color',
        help='Color for UI display'
    )

    # Constraints (Odoo 19 style)
    _check_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Tag name must be unique!',
    )

