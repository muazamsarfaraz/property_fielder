# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class UtilityMeter(models.Model):
    _name = 'property_fielder.utility.meter'
    _description = 'Property Utility Meter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'property_id, utility_type'

    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    utility_type = fields.Selection([
        ('electricity', 'Electricity'),
        ('gas', 'Gas'),
        ('water', 'Water'),
        ('district_heat', 'District Heating'),
        ('solar', 'Solar/PV')
    ], string='Utility Type', required=True, tracking=True)
    
    # UK-Specific Meter Identifiers
    meter_serial = fields.Char(string='Meter Serial Number', tracking=True)
    mpan = fields.Char(
        string='MPAN',
        help='Meter Point Administration Number - 13 digit electricity supply identifier'
    )
    mprn = fields.Char(
        string='MPRN',
        help='Meter Point Reference Number - gas supply identifier'
    )
    spid = fields.Char(
        string='SPID',
        help='Supply Point ID - water supply identifier (Scotland)'
    )
    
    # Meter Details
    meter_type = fields.Selection([
        ('standard', 'Standard'),
        ('prepayment', 'Prepayment'),
        ('smart', 'Smart Meter'),
        ('economy7', 'Economy 7'),
        ('economy10', 'Economy 10')
    ], string='Meter Type', default='standard')
    
    meter_location = fields.Char(
        string='Meter Location',
        help='Physical location of the meter (e.g., "Under stairs", "External box")'
    )
    
    # Supplier Information
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        help='Current utility supplier'
    )
    account_number = fields.Char(string='Account Number')
    tariff_name = fields.Char(string='Tariff Name')
    contract_end_date = fields.Date(string='Contract End Date', tracking=True)
    
    # Current Status
    is_active = fields.Boolean(string='Active', default=True)
    is_responsible = fields.Boolean(
        string='Landlord Responsible',
        default=False,
        help='If true, landlord pays this utility (common in HMOs)'
    )
    
    # Readings
    reading_ids = fields.One2many(
        'property_fielder.meter.reading',
        'meter_id',
        string='Readings'
    )
    last_reading = fields.Float(
        string='Last Reading',
        compute='_compute_last_reading',
        store=True
    )
    last_reading_date = fields.Date(
        string='Last Reading Date',
        compute='_compute_last_reading',
        store=True
    )
    
    notes = fields.Text(string='Notes')
    
    @api.depends('reading_ids', 'reading_ids.reading_value', 'reading_ids.reading_date')
    def _compute_last_reading(self):
        for meter in self:
            readings = meter.reading_ids.sorted(key=lambda r: r.reading_date, reverse=True)
            if readings:
                meter.last_reading = readings[0].reading_value
                meter.last_reading_date = readings[0].reading_date
            else:
                meter.last_reading = 0
                meter.last_reading_date = False

    @api.constrains('mpan')
    def _check_mpan(self):
        """Validate MPAN format (13 digits)"""
        import re
        for meter in self:
            if meter.mpan:
                clean_mpan = re.sub(r'[\s\-]', '', meter.mpan)
                if not re.match(r'^\d{13}$', clean_mpan):
                    raise ValidationError(
                        _('MPAN must be exactly 13 digits. Got: %s') % meter.mpan
                    )

    def action_record_reading(self):
        """Open wizard to record a new meter reading"""
        self.ensure_one()
        return {
            'name': _('Record Meter Reading'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.meter.reading',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_meter_id': self.id},
        }


class MeterReading(models.Model):
    _name = 'property_fielder.meter.reading'
    _description = 'Meter Reading'
    _order = 'reading_date desc, id desc'

    meter_id = fields.Many2one(
        'property_fielder.utility.meter',
        string='Meter',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    reading_date = fields.Date(
        string='Reading Date',
        required=True,
        default=fields.Date.today
    )
    reading_value = fields.Float(string='Reading Value', required=True)
    
    reading_type = fields.Selection([
        ('actual', 'Actual Reading'),
        ('estimated', 'Estimated'),
        ('opening', 'Opening Reading'),
        ('closing', 'Closing Reading')
    ], string='Reading Type', default='actual', required=True)
    
    read_by_id = fields.Many2one('res.partner', string='Read By')
    photo = fields.Image(string='Meter Photo', max_width=1920, max_height=1920)
    notes = fields.Text(string='Notes')
    
    # Related property
    property_id = fields.Many2one(
        related='meter_id.property_id',
        store=True,
        string='Property'
    )

