# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InspectionChecklistTemplate(models.Model):
    """Template for inspection checklists linked to certification types."""
    _name = 'property_fielder.checklist.template'
    _description = 'Inspection Checklist Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    certification_type_id = fields.Many2one(
        'property_fielder.certification.type',
        string='Certification Type',
        required=True,
        ondelete='cascade',
        help='The certification type this checklist applies to'
    )
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    
    # Template Items
    item_ids = fields.One2many(
        'property_fielder.checklist.template.item',
        'template_id',
        string='Checklist Items'
    )
    item_count = fields.Integer(compute='_compute_item_count')
    
    @api.depends('item_ids')
    def _compute_item_count(self):
        for template in self:
            template.item_count = len(template.item_ids)


class InspectionChecklistTemplateItem(models.Model):
    """Template item for an inspection checklist."""
    _name = 'property_fielder.checklist.template.item'
    _description = 'Checklist Template Item'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'property_fielder.checklist.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Item Description', required=True)
    
    # Item Type
    item_type = fields.Selection([
        ('check', 'Pass/Fail Check'),
        ('reading', 'Reading/Measurement'),
        ('text', 'Text Input'),
        ('photo', 'Photo Required')
    ], string='Item Type', default='check', required=True)
    
    # Category/Section
    category = fields.Char(string='Section/Category')
    
    # Requirements
    is_mandatory = fields.Boolean(
        string='Mandatory',
        default=False,
        help='If checked, this item must be completed for inspection to pass'
    )
    
    # For reading type items
    reading_unit = fields.Char(string='Unit of Measurement', help='e.g., ppm, %, °C, mbar')
    reading_min = fields.Float(string='Minimum Acceptable Value')
    reading_max = fields.Float(string='Maximum Acceptable Value')
    
    # Help text
    help_text = fields.Text(string='Instructions', help='Instructions for the inspector')


class InspectionChecklistItem(models.Model):
    """Actual checklist item for an inspection."""
    _name = 'property_fielder.inspection.checklist.item'
    _description = 'Inspection Checklist Item'
    _order = 'sequence, id'

    inspection_id = fields.Many2one(
        'property_fielder.property.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade'
    )
    template_item_id = fields.Many2one(
        'property_fielder.checklist.template.item',
        string='Template Item',
        ondelete='set null'
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Item Description', required=True)
    category = fields.Char(string='Section/Category')
    
    # Item Type
    item_type = fields.Selection([
        ('check', 'Pass/Fail Check'),
        ('reading', 'Reading/Measurement'),
        ('text', 'Text Input'),
        ('photo', 'Photo Required')
    ], string='Item Type', default='check', required=True)
    
    # Result
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('na', 'N/A'),
        ('pending', 'Pending')
    ], string='Result', default='pending')
    
    # Requirements
    is_mandatory = fields.Boolean(string='Mandatory', default=False)
    
    # For reading type
    reading_value = fields.Float(string='Reading Value')
    reading_unit = fields.Char(string='Unit')
    reading_min = fields.Float(string='Min Acceptable')
    reading_max = fields.Float(string='Max Acceptable')
    reading_in_range = fields.Boolean(
        string='In Range',
        compute='_compute_reading_in_range',
        store=True
    )
    
    # For text type
    text_value = fields.Text(string='Text Value')
    
    # Notes and defects
    notes = fields.Text(string='Notes')
    has_defect = fields.Boolean(string='Has Defect', default=False)
    defect_severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Defect Severity')
    defect_description = fields.Text(string='Defect Description')
    remediation_required = fields.Boolean(string='Remediation Required', default=False)
    
    # Help text (from template)
    help_text = fields.Text(string='Instructions')
    
    @api.depends('reading_value', 'reading_min', 'reading_max', 'item_type')
    def _compute_reading_in_range(self):
        for item in self:
            if item.item_type == 'reading' and item.reading_value:
                item.reading_in_range = (
                    (not item.reading_min or item.reading_value >= item.reading_min) and
                    (not item.reading_max or item.reading_value <= item.reading_max)
                )
            else:
                item.reading_in_range = True

