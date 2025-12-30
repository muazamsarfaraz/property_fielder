# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class InspectionPhoto(models.Model):
    """Structured inspection photo with categorization and metadata."""
    _name = 'property_fielder.inspection.photo'
    _description = 'Inspection Photo'
    _order = 'sequence, id'

    name = fields.Char(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Image
    image = fields.Image(string='Photo', required=True, max_width=1920, max_height=1920)
    image_medium = fields.Image(
        string='Medium Image',
        max_width=512,
        max_height=512,
        related='image',
        store=True
    )
    image_small = fields.Image(
        string='Thumbnail',
        max_width=128,
        max_height=128,
        related='image',
        store=True
    )
    
    # Relationships
    inspection_id = fields.Many2one(
        'property_fielder.property.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade'
    )
    property_id = fields.Many2one(
        related='inspection_id.property_id',
        store=True,
        string='Property'
    )
    
    # Photo Category
    category = fields.Selection([
        ('general', 'General'),
        ('before', 'Before'),
        ('after', 'After'),
        ('damage', 'Damage/Defect'),
        ('remediation', 'Remediation/Repair'),
        ('evidence', 'Evidence/Documentation'),
        ('hazard', 'Hazard'),
        ('equipment', 'Equipment'),
        ('meter', 'Meter Reading'),
        ('access', 'Access Point'),
        ('certificate', 'Certificate/Label')
    ], string='Category', default='general', required=True)
    
    # Before/After Pairing
    is_before = fields.Boolean(string='Is Before Photo', compute='_compute_before_after', store=True)
    is_after = fields.Boolean(string='Is After Photo', compute='_compute_before_after', store=True)
    paired_photo_id = fields.Many2one(
        'property_fielder.inspection.photo',
        string='Paired Photo',
        help='Link to corresponding before/after photo'
    )
    
    # Location/Context
    location = fields.Char(
        string='Location',
        help='Location within property (e.g., "Kitchen", "Master Bedroom")'
    )
    room = fields.Selection([
        ('kitchen', 'Kitchen'),
        ('living_room', 'Living Room'),
        ('bedroom', 'Bedroom'),
        ('bathroom', 'Bathroom'),
        ('hallway', 'Hallway'),
        ('garage', 'Garage'),
        ('garden', 'Garden'),
        ('boiler_room', 'Boiler Room'),
        ('utility', 'Utility Room'),
        ('loft', 'Loft/Attic'),
        ('basement', 'Basement'),
        ('exterior', 'Exterior'),
        ('communal', 'Communal Area'),
        ('other', 'Other')
    ], string='Room')
    
    # Annotations/Notes
    annotations = fields.Text(
        string='Annotations',
        help='Text annotations describing what is shown in the photo'
    )
    
    # Metadata
    taken_date = fields.Datetime(
        string='Date Taken',
        default=fields.Datetime.now
    )
    taken_by_id = fields.Many2one(
        'property_fielder.inspector',
        string='Taken By',
        help='Inspector who took the photo'
    )
    
    # Severity (for damage/hazard photos)
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity', help='Severity level for damage/hazard photos')
    
    # GPS coordinates (for mobile capture)
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    # Status
    requires_action = fields.Boolean(
        string='Requires Action',
        default=False,
        help='Mark if this photo documents an issue requiring follow-up'
    )
    action_taken = fields.Text(string='Action Taken')
    
    @api.depends('category')
    def _compute_before_after(self):
        for photo in self:
            photo.is_before = photo.category == 'before'
            photo.is_after = photo.category == 'after'
    
    @api.model
    def create(self, vals):
        # Set taken_by to current user's inspector if available
        if not vals.get('taken_by_id'):
            inspector = self.env['property_fielder.inspector'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            if inspector:
                vals['taken_by_id'] = inspector.id
        return super().create(vals)

