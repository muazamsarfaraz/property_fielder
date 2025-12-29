# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta


class PropertyAsset(models.Model):
    """Property Assets - appliances, fixtures, and equipment.
    
    Tracks items provided with rental properties that may require
    maintenance, PAT testing, or replacement scheduling.
    """
    _name = 'property_fielder.property.asset'
    _description = 'Property Asset/Appliance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'property_id, asset_type, name'

    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    name = fields.Char(string='Asset Name', required=True)
    
    asset_type = fields.Selection([
        ('white_goods', 'White Goods'),
        ('heating', 'Heating/Boiler'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('fire_safety', 'Fire Safety'),
        ('security', 'Security'),
        ('furniture', 'Furniture'),
        ('other', 'Other')
    ], string='Asset Type', required=True)
    
    asset_category = fields.Selection([
        ('boiler', 'Boiler'),
        ('cooker', 'Cooker/Hob'),
        ('fridge', 'Fridge/Freezer'),
        ('washing_machine', 'Washing Machine'),
        ('dryer', 'Tumble Dryer'),
        ('dishwasher', 'Dishwasher'),
        ('water_heater', 'Water Heater'),
        ('smoke_alarm', 'Smoke Alarm'),
        ('co_alarm', 'CO Alarm'),
        ('heat_alarm', 'Heat Alarm'),
        ('fire_extinguisher', 'Fire Extinguisher'),
        ('fire_blanket', 'Fire Blanket'),
        ('thermostat', 'Thermostat'),
        ('radiator', 'Radiator'),
        ('door_lock', 'Door Lock'),
        ('window', 'Window'),
        ('other', 'Other')
    ], string='Category')
    
    # Details
    manufacturer = fields.Char(string='Manufacturer/Brand')
    model_number = fields.Char(string='Model Number')
    serial_number = fields.Char(string='Serial Number')
    
    # Location
    location = fields.Char(
        string='Location',
        help='e.g., Kitchen, Bedroom 1, Hallway'
    )
    
    # Acquisition
    purchase_date = fields.Date(string='Purchase Date')
    purchase_price = fields.Monetary(
        string='Purchase Price',
        currency_field='currency_id'
    )
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Warranty
    warranty_expiry = fields.Date(string='Warranty Expires')
    warranty_document = fields.Binary(string='Warranty Document', attachment=True)
    warranty_filename = fields.Char(string='Warranty Filename')
    
    # Status
    state = fields.Selection([
        ('active', 'Active/Working'),
        ('repair_needed', 'Repair Needed'),
        ('under_repair', 'Under Repair'),
        ('replaced', 'Replaced'),
        ('disposed', 'Disposed')
    ], string='Status', default='active', tracking=True)
    
    # Maintenance
    last_service_date = fields.Date(string='Last Service Date')
    next_service_date = fields.Date(string='Next Service Due')
    service_interval_months = fields.Integer(
        string='Service Interval (Months)',
        default=12
    )
    
    # PAT Testing (for electrical items)
    requires_pat = fields.Boolean(
        string='Requires PAT Test',
        help='Portable Appliance Testing required'
    )
    last_pat_date = fields.Date(string='Last PAT Test')
    next_pat_date = fields.Date(string='Next PAT Due')
    pat_passed = fields.Boolean(string='PAT Passed')
    
    # Expected Life
    expected_life_years = fields.Integer(
        string='Expected Life (Years)',
        help='Expected lifespan for depreciation/replacement planning'
    )
    replacement_due = fields.Date(
        string='Replacement Due',
        compute='_compute_replacement_due',
        store=True
    )
    
    # Documentation
    manual = fields.Binary(string='Manual/Instructions', attachment=True)
    manual_filename = fields.Char(string='Manual Filename')
    photo = fields.Image(string='Photo', max_width=1920, max_height=1920)
    
    notes = fields.Text(string='Notes')

    @api.depends('purchase_date', 'expected_life_years')
    def _compute_replacement_due(self):
        for asset in self:
            if asset.purchase_date and asset.expected_life_years:
                asset.replacement_due = asset.purchase_date + timedelta(
                    days=365 * asset.expected_life_years
                )
            else:
                asset.replacement_due = False

    @api.onchange('last_service_date', 'service_interval_months')
    def _onchange_service_date(self):
        if self.last_service_date and self.service_interval_months:
            self.next_service_date = self.last_service_date + timedelta(
                days=30 * self.service_interval_months
            )

