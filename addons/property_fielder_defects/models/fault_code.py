# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FaultCode(models.Model):
    """Industry standard fault codes for defect classification."""
    
    _name = 'property_fielder.fault.code'
    _description = 'Fault Code'
    _order = 'category, sequence, code'
    
    name = fields.Char(
        string='Name',
        required=True,
        help='Full name of the fault code'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Industry standard code (e.g., ID, AR, C1, C2)'
    )
    category = fields.Selection([
        ('gas', 'Gas Safety'),
        ('electrical', 'Electrical'),
        ('fire', 'Fire Safety'),
        ('legionella', 'Legionella'),
        ('asbestos', 'Asbestos'),
        ('general', 'General'),
    ], string='Category', required=True, default='general')
    
    industry_standard = fields.Char(
        string='Industry Standard',
        help='Reference standard (e.g., GIUSP, 18th Edition, RRO 2005)'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of this fault code'
    )
    
    severity_sla = fields.Selection([
        ('immediate', 'Immediate (24 hours)'),
        ('urgent', 'Urgent (7 days)'),
        ('standard', 'Standard (28 days)'),
        ('advisory', 'Advisory (No SLA)'),
    ], string='Severity SLA', required=True, default='standard',
       help='SLA severity level for deadline calculation')
    
    remediation_hours = fields.Integer(
        string='Remediation Hours',
        compute='_compute_remediation_hours',
        store=True,
        help='Hours allowed for remediation based on severity'
    )
    
    requires_immediate_action = fields.Boolean(
        string='Requires Immediate Action',
        default=False,
        help='Must take immediate action on-site (e.g., isolate gas supply)'
    )
    
    action_required = fields.Text(
        string='Action Required',
        help='Description of required action for this fault code'
    )
    
    photo_mandatory = fields.Boolean(
        string='Photo Mandatory',
        default=True,
        help='Photo evidence is mandatory for this fault code'
    )
    
    certification_type_id = fields.Many2one(
        'property_fielder.certification.type',
        string='Certification Type',
        help='Associated certification type'
    )
    
    sequence = fields.Integer(string='Sequence', default=10)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

    # Constraints (Odoo 19 style)
    _check_code_category_unique = models.Constraint(
        'UNIQUE(code, category)',
        'Fault code must be unique within each category!',
    )
    
    @api.depends('severity_sla')
    def _compute_remediation_hours(self):
        """Compute remediation hours based on severity SLA."""
        sla_hours = {
            'immediate': 24,
            'urgent': 168,  # 7 days
            'standard': 672,  # 28 days
            'advisory': 0,  # No SLA
        }
        for record in self:
            record.remediation_hours = sla_hours.get(record.severity_sla, 0)
    
    def name_get(self):
        """Display as 'CODE - Name'."""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            result.append((record.id, name))
        return result

