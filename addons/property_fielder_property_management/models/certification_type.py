# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CertificationType(models.Model):
    _name = 'property_fielder.certification.type'
    _description = 'Certification Type'
    _order = 'sequence, name'

    name = fields.Char(string='Certification Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', translate=True)
    
    # FLAGE+ Category
    flage_category = fields.Selection([
        ('fire', 'F - Fire Safety'),
        ('legionella', 'L - Legionella Control'),
        ('asbestos', 'A - Asbestos Management'),
        ('gas', 'G - Gas Safety'),
        ('electrical', 'E - Electrical Safety'),
        ('other', 'Other')
    ], string='FLAGE+ Category', required=True)
    
    # Validity Configuration
    validity_period = fields.Integer(
        string='Validity Period (Days)',
        required=True,
        default=365,
        help='Number of days the certification is valid for'
    )

    warning_period = fields.Integer(
        string='Warning Period (Days)',
        default=30,
        help='Number of days before expiry to show warning'
    )

    # Inspection Duration
    default_duration_minutes = fields.Integer(
        string='Default Inspection Duration (minutes)',
        required=True,
        default=60,
        help='Default time required to complete an inspection of this type'
    )
    
    # Requirements
    requirement_ids = fields.One2many(
        'property_fielder.compliance.requirement',
        'certification_type_id',
        string='Requirements'
    )
    
    # Display
    color = fields.Integer(string='Color Index')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Statistics
    certification_count = fields.Integer(
        string='Certifications',
        compute='_compute_certification_count'
    )
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Certification code must be unique!'),
    ]

    def _compute_certification_count(self):
        for cert_type in self:
            cert_type.certification_count = self.env['property_fielder.property.certification'].search_count([
                ('certification_type_id', '=', cert_type.id)
            ])


class ComplianceRequirement(models.Model):
    _name = 'property_fielder.compliance.requirement'
    _description = 'Compliance Requirement'
    _order = 'sequence, name'

    name = fields.Char(string='Requirement', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    
    certification_type_id = fields.Many2one(
        'property_fielder.certification.type',
        string='Certification Type',
        required=True,
        ondelete='cascade'
    )
    
    # Requirement Details
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    legal_reference = fields.Char(string='Legal Reference')
    
    # Inspection Configuration
    inspection_frequency = fields.Selection([
        ('annual', 'Annual'),
        ('biannual', 'Bi-Annual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom')
    ], string='Inspection Frequency')
    
    custom_frequency_days = fields.Integer(
        string='Custom Frequency (Days)',
        help='Only used when inspection frequency is Custom'
    )
    
    # Documentation
    document_required = fields.Boolean(string='Document Required', default=True)
    document_template = fields.Binary(string='Document Template', attachment=True)
    document_template_filename = fields.Char()
    
    # Display
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes')

