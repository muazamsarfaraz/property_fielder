# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DefectPhoto(models.Model):
    """Photo evidence for defects with before/after categorization."""
    
    _name = 'property_fielder.defect.photo'
    _description = 'Defect Photo'
    _order = 'photo_type, sequence, create_date'
    
    defect_id = fields.Many2one(
        'property_fielder.defect',
        string='Defect',
        required=True,
        ondelete='cascade'
    )
    
    property_id = fields.Many2one(
        related='defect_id.property_id',
        store=True,
        string='Property'
    )
    
    name = fields.Char(
        string='Description',
        help='Brief description of what the photo shows'
    )
    
    image = fields.Image(
        string='Photo',
        required=True,
        max_width=1920,
        max_height=1920
    )
    
    image_thumbnail = fields.Image(
        string='Thumbnail',
        related='image',
        max_width=256,
        max_height=256,
        store=True
    )
    
    photo_type = fields.Selection([
        ('before', 'Before (Defect)'),
        ('during', 'During (Work in Progress)'),
        ('after', 'After (Remediation)'),
        ('evidence', 'Evidence'),
    ], string='Photo Type', required=True, default='before')
    
    category = fields.Selection([
        ('damage', 'Damage'),
        ('remediation', 'Remediation'),
        ('evidence', 'Evidence'),
        ('access', 'Access Issue'),
        ('other', 'Other'),
    ], string='Category', default='damage')
    
    location = fields.Char(
        string='Location',
        help='Where in the property this photo was taken'
    )
    
    annotation = fields.Text(
        string='Annotation',
        help='Notes or annotations for this photo'
    )
    
    taken_date = fields.Datetime(
        string='Taken Date',
        default=fields.Datetime.now
    )
    
    taken_by = fields.Many2one(
        'res.users',
        string='Taken By',
        default=lambda self: self.env.user
    )
    
    # GPS coordinates if available
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    def name_get(self):
        result = []
        for record in self:
            name = record.name or f"{record.photo_type.title()} Photo"
            result.append((record.id, name))
        return result

