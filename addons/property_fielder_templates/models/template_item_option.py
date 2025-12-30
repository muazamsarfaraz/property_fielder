# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TemplateItemOption(models.Model):
    """Options for select_one/select_multi response types"""
    
    _name = 'property_fielder.inspection.template.item.option'
    _description = 'Template Item Option'
    _order = 'sequence, id'
    
    # Parent Item
    item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Item',
        required=True,
        ondelete='cascade',
        help='Parent item'
    )
    
    # Basic Information
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    
    value = fields.Char(
        string='Value',
        required=True,
        help='Internal value (stored in response)'
    )
    
    label = fields.Char(
        string='Label',
        required=True,
        translate=True,
        help='Display label (translatable)'
    )
    
    # Defect Trigger
    is_failure = fields.Boolean(
        string='Is Failure',
        default=False,
        help='This option triggers defect creation'
    )
    
    # UI Styling
    color = fields.Char(
        string='Color',
        default='#4CAF50',
        help='UI color hint (e.g., #FF0000 for fail)'
    )
    
    icon = fields.Char(
        string='Icon',
        help='FontAwesome icon class (e.g., fa-check)'
    )
    
    # Score value for calculations
    score = fields.Integer(
        string='Score',
        default=0,
        help='Score value for this option (for calculations)'
    )
    
    # Display name
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.label or record.value))
        return result

