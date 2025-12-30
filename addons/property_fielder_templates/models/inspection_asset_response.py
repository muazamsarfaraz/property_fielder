# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InspectionAssetResponse(models.Model):
    """Asset-Level Inspection Response - For CP12/EICR where multiple assets are tested"""
    
    _name = 'property_fielder.inspection.asset.response'
    _description = 'Inspection Asset Response'
    _order = 'sequence, id'
    
    # Parent Inspection
    inspection_id = fields.Many2one(
        'property_fielder.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade',
        help='Parent inspection'
    )
    
    # Sequence (order in the inspection)
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of this asset'
    )
    
    # Existing Asset (from property)
    asset_id = fields.Many2one(
        'property_fielder.property.asset',
        string='Property Asset',
        help='Linked property asset (if exists)'
    )
    
    # Asset details (can be entered during inspection for new assets)
    asset_name = fields.Char(
        string='Asset Name',
        help='Name of the asset (for new assets discovered during inspection)'
    )
    
    asset_type = fields.Selection([
        ('gas_boiler', 'Gas Boiler'),
        ('gas_fire', 'Gas Fire'),
        ('gas_cooker', 'Gas Cooker'),
        ('gas_hob', 'Gas Hob'),
        ('gas_water_heater', 'Gas Water Heater'),
        ('gas_other', 'Other Gas Appliance'),
        ('circuit_ring', 'Ring Main Circuit'),
        ('circuit_lighting', 'Lighting Circuit'),
        ('circuit_cooker', 'Cooker Circuit'),
        ('circuit_shower', 'Shower Circuit'),
        ('circuit_other', 'Other Circuit'),
        ('fire_door', 'Fire Door'),
        ('smoke_detector', 'Smoke Detector'),
        ('co_detector', 'CO Detector'),
        ('heat_detector', 'Heat Detector'),
        ('appliance_general', 'General Appliance'),
    ], string='Asset Type', help='Type of asset being inspected')
    
    # Asset identification
    asset_location = fields.Char(
        string='Location',
        help='Where the asset is located (e.g., Kitchen, Main Bedroom)'
    )
    
    asset_make = fields.Char(
        string='Make',
        help='Manufacturer'
    )
    
    asset_model = fields.Char(
        string='Model',
        help='Model number'
    )
    
    asset_serial = fields.Char(
        string='Serial Number',
        help='Serial number'
    )
    
    # Responses for this asset
    response_ids = fields.One2many(
        'property_fielder.inspection.response',
        'asset_response_id',
        string='Responses',
        help='Responses for this asset'
    )
    
    # Overall result for this asset
    overall_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('na', 'N/A'),
    ], string='Result', default='na', help='Overall result for this asset')
    
    # Gas specific fields
    gas_flue_type = fields.Selection([
        ('open_flue', 'Open Flue'),
        ('room_sealed', 'Room Sealed'),
        ('flueless', 'Flueless'),
    ], string='Flue Type')
    
    gas_combustion_reading = fields.Float(
        string='Combustion Reading',
        help='Combustion analyzer reading'
    )
    
    # Electrical specific fields
    electrical_circuit_rating = fields.Char(
        string='Circuit Rating',
        help='Rating (e.g., 32A)'
    )
    
    electrical_rcd_protected = fields.Boolean(
        string='RCD Protected',
        default=False
    )
    
    # Notes
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this asset'
    )
    
    # Display name
    def name_get(self):
        result = []
        for record in self:
            name = record.asset_name or (record.asset_id.name if record.asset_id else 'Asset')
            if record.asset_location:
                name = '%s (%s)' % (name, record.asset_location)
            result.append((record.id, name))
        return result
    
    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        """Copy details from linked asset."""
        if self.asset_id:
            self.asset_name = self.asset_id.name
            self.asset_make = self.asset_id.manufacturer
            self.asset_model = self.asset_id.model
            self.asset_serial = self.asset_id.serial_number

