# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HMORoom(models.Model):
    """HMO Room Details.
    
    Tracks individual rooms in HMO properties with minimum space
    standards compliance per The Licensing of Houses in Multiple 
    Occupation (Mandatory Conditions of Licences) (England) Regulations 2018.
    """
    _name = 'property_fielder.hmo.room'
    _description = 'HMO Room'
    _order = 'property_id, floor_level, room_number'

    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True,
        domain=[('hmo_status', '!=', 'not_hmo')]
    )
    
    room_number = fields.Char(string='Room Number/Name', required=True)
    
    room_type = fields.Selection([
        ('bedroom', 'Bedroom'),
        ('bedsit', 'Bedsit/Studio'),
        ('kitchen', 'Kitchen'),
        ('bathroom', 'Bathroom'),
        ('toilet', 'Separate WC'),
        ('living', 'Living Room'),
        ('utility', 'Utility Room'),
        ('communal', 'Communal Area'),
        ('other', 'Other')
    ], string='Room Type', required=True)
    
    floor_level = fields.Integer(
        string='Floor Level',
        default=0,
        help='0=Ground, 1=First, -1=Basement'
    )
    
    # Dimensions
    length_m = fields.Float(string='Length (m)', digits=(6, 2))
    width_m = fields.Float(string='Width (m)', digits=(6, 2))
    floor_area_sqm = fields.Float(
        string='Floor Area (sqm)',
        compute='_compute_floor_area',
        store=True
    )
    ceiling_height_m = fields.Float(
        string='Ceiling Height (m)',
        digits=(4, 2),
        default=2.4
    )
    
    # Occupancy
    max_occupancy = fields.Integer(
        string='Maximum Occupancy',
        compute='_compute_max_occupancy',
        store=True,
        help='Based on minimum space standards'
    )
    current_occupancy = fields.Integer(
        string='Current Occupancy',
        default=0
    )
    tenant_id = fields.Many2one(
        'res.partner',
        string='Current Tenant'
    )
    
    # Facilities
    has_cooking = fields.Boolean(string='Has Cooking Facilities')
    has_sink = fields.Boolean(string='Has Sink')
    has_heating = fields.Boolean(string='Has Heating')
    has_window = fields.Boolean(string='Has Window')
    window_openable = fields.Boolean(string='Window Openable')
    has_smoke_alarm = fields.Boolean(string='Has Smoke Alarm')
    
    # Fire Safety
    fire_door = fields.Boolean(string='Fire Door Fitted')
    fire_door_rating = fields.Selection([
        ('fd30', 'FD30 (30 min)'),
        ('fd60', 'FD60 (60 min)'),
        ('none', 'Standard Door')
    ], string='Fire Door Rating', default='none')
    escape_route_clear = fields.Boolean(string='Escape Route Clear')
    
    # Compliance
    compliant = fields.Boolean(
        string='Meets Minimum Standards',
        compute='_compute_compliance',
        store=True
    )
    compliance_issues = fields.Text(
        string='Compliance Issues',
        compute='_compute_compliance',
        store=True
    )
    
    # Rent
    weekly_rent = fields.Monetary(
        string='Weekly Rent',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    notes = fields.Text(string='Notes')

    @api.depends('length_m', 'width_m')
    def _compute_floor_area(self):
        for room in self:
            room.floor_area_sqm = room.length_m * room.width_m

    @api.depends('floor_area_sqm', 'room_type')
    def _compute_max_occupancy(self):
        """Compute max occupancy based on UK minimum space standards.
        
        2018 Regulations minimum sleeping room sizes:
        - 6.51 sqm for 1 person over 10
        - 10.22 sqm for 2 persons over 10
        - 4.64 sqm for 1 child under 10
        """
        for room in self:
            if room.room_type not in ('bedroom', 'bedsit'):
                room.max_occupancy = 0
            elif room.floor_area_sqm >= 10.22:
                room.max_occupancy = 2
            elif room.floor_area_sqm >= 6.51:
                room.max_occupancy = 1
            else:
                room.max_occupancy = 0  # Below minimum

    @api.depends('floor_area_sqm', 'max_occupancy', 'room_type', 'has_window', 
                 'has_heating', 'fire_door', 'has_smoke_alarm')
    def _compute_compliance(self):
        """Check room meets minimum HMO standards"""
        for room in self:
            issues = []
            
            if room.room_type in ('bedroom', 'bedsit'):
                if room.floor_area_sqm < 6.51:
                    issues.append(f'Room too small: {room.floor_area_sqm:.1f}sqm (min 6.51sqm)')
                if not room.has_window:
                    issues.append('No window')
                if not room.has_heating:
                    issues.append('No heating')
            
            if room.room_type == 'bedroom' and not room.fire_door:
                issues.append('Fire door required')
            
            if room.room_type in ('bedroom', 'bedsit', 'living') and not room.has_smoke_alarm:
                issues.append('Smoke alarm required')
            
            room.compliance_issues = '\n'.join(issues) if issues else ''
            room.compliant = len(issues) == 0

