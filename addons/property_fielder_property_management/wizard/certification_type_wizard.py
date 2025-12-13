# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CertificationTypeWizard(models.TransientModel):
    _name = 'property_fielder.certification.type.wizard'
    _description = 'Quick Create Certification Type'

    # Template Selection
    template = fields.Selection([
        ('custom', 'Custom Certification'),
        ('boiler', 'Boiler Service Certificate'),
        ('lift', 'Lift Inspection Certificate'),
        ('fire_ext', 'Fire Extinguisher Service'),
        ('emergency_light', 'Emergency Lighting Test'),
        ('water_tank', 'Water Tank Cleaning'),
        ('playground', 'Playground Safety Inspection'),
        ('cctv', 'CCTV Maintenance'),
        ('gutter', 'Gutter Cleaning'),
        ('roof', 'Roof Inspection'),
        ('drainage', 'Drainage System Check'),
        ('alarm', 'Burglar Alarm Service'),
        ('door_entry', 'Door Entry System Service'),
    ], string='Certification Template', required=True, default='custom')
    
    # Basic Fields
    name = fields.Char(string='Certification Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    flage_category = fields.Selection([
        ('fire', 'F - Fire Safety'),
        ('legionella', 'L - Legionella Control'),
        ('asbestos', 'A - Asbestos Management'),
        ('gas', 'G - Gas Safety'),
        ('electrical', 'E - Electrical Safety'),
        ('other', 'Other')
    ], string='FLAGE+ Category', required=True, default='other')
    
    # Validity Configuration
    validity_period = fields.Integer(
        string='Validity Period (Days)',
        required=True,
        default=365
    )
    warning_period = fields.Integer(
        string='Warning Period (Days)',
        required=True,
        default=30
    )
    default_duration_minutes = fields.Integer(
        string='Default Inspection Duration (minutes)',
        required=True,
        default=60,
        help='Default time required to complete an inspection of this type'
    )
    
    @api.onchange('template')
    def _onchange_template(self):
        """Auto-fill fields based on template selection"""
        templates = {
            'boiler': {
                'name': 'Boiler Service Certificate',
                'code': 'BOILER',
                'description': 'Annual boiler service and safety check',
                'flage_category': 'gas',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 45,
            },
            'lift': {
                'name': 'Lift Inspection Certificate',
                'code': 'LIFT',
                'description': '6-monthly lift safety inspection (LOLER)',
                'flage_category': 'other',
                'validity_period': 180,
                'warning_period': 30,
                'default_duration_minutes': 60,
            },
            'fire_ext': {
                'name': 'Fire Extinguisher Service',
                'code': 'FIRE_EXT',
                'description': 'Annual fire extinguisher inspection and service',
                'flage_category': 'fire',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 30,
            },
            'emergency_light': {
                'name': 'Emergency Lighting Test',
                'code': 'EMERG_LIGHT',
                'description': 'Annual emergency lighting system test',
                'flage_category': 'fire',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 45,
            },
            'water_tank': {
                'name': 'Water Tank Cleaning',
                'code': 'WATER_TANK',
                'description': 'Annual water tank cleaning and disinfection',
                'flage_category': 'legionella',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 90,
            },
            'playground': {
                'name': 'Playground Safety Inspection',
                'code': 'PLAYGROUND',
                'description': 'Annual playground equipment safety inspection',
                'flage_category': 'other',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 60,
            },
            'cctv': {
                'name': 'CCTV Maintenance',
                'code': 'CCTV',
                'description': 'Annual CCTV system maintenance and check',
                'flage_category': 'other',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 45,
            },
            'gutter': {
                'name': 'Gutter Cleaning',
                'code': 'GUTTER',
                'description': 'Bi-annual gutter cleaning and inspection',
                'flage_category': 'other',
                'validity_period': 180,
                'warning_period': 30,
                'default_duration_minutes': 30,
            },
            'roof': {
                'name': 'Roof Inspection',
                'code': 'ROOF',
                'description': 'Annual roof condition inspection',
                'flage_category': 'other',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 60,
            },
            'drainage': {
                'name': 'Drainage System Check',
                'code': 'DRAINAGE',
                'description': 'Annual drainage system inspection and cleaning',
                'flage_category': 'other',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 45,
            },
            'alarm': {
                'name': 'Burglar Alarm Service',
                'code': 'ALARM',
                'description': 'Annual burglar alarm system service',
                'flage_category': 'other',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 30,
            },
            'door_entry': {
                'name': 'Door Entry System Service',
                'code': 'DOOR_ENTRY',
                'description': 'Annual door entry system maintenance',
                'flage_category': 'other',
                'validity_period': 365,
                'warning_period': 60,
                'default_duration_minutes': 30,
            },
        }

        if self.template and self.template != 'custom':
            template_data = templates.get(self.template, {})
            self.name = template_data.get('name', '')
            self.code = template_data.get('code', '')
            self.description = template_data.get('description', '')
            self.flage_category = template_data.get('flage_category', 'other')
            self.validity_period = template_data.get('validity_period', 365)
            self.warning_period = template_data.get('warning_period', 30)
            self.default_duration_minutes = template_data.get('default_duration_minutes', 60)
    
    def action_create_certification_type(self):
        """Create the certification type"""
        self.ensure_one()
        
        # Check if code already exists
        existing = self.env['property_fielder.certification.type'].search([
            ('code', '=', self.code)
        ])
        if existing:
            raise UserError(_('A certification type with code "%s" already exists!') % self.code)
        
        # Create certification type
        cert_type = self.env['property_fielder.certification.type'].create({
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'flage_category': self.flage_category,
            'validity_period': self.validity_period,
            'warning_period': self.warning_period,
            'default_duration_minutes': self.default_duration_minutes,
        })
        
        # Return action to open the created certification type
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.certification.type',
            'res_id': cert_type.id,
            'view_mode': 'form',
            'target': 'current',
        }

