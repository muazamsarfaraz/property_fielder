# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TemplateSection(models.Model):
    """Template Section - Groups inspection items"""
    
    _name = 'property_fielder.inspection.template.section'
    _description = 'Template Section'
    _order = 'sequence, id'
    
    # Parent Template
    template_id = fields.Many2one(
        'property_fielder.inspection.template',
        string='Template',
        required=True,
        ondelete='cascade',
        help='Parent template'
    )
    
    # Basic Information
    name = fields.Char(
        string='Section Name',
        required=True,
        help='Name of the section'
    )
    
    code = fields.Char(
        string='Section Code',
        help='Unique code for reference in skip logic'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    
    description = fields.Text(
        string='Description',
        help='Guidance text for this section'
    )
    
    # Items in this section
    item_ids = fields.One2many(
        'property_fielder.inspection.template.item',
        'section_id',
        string='Items',
        copy=True,
        help='Items in this section'
    )
    
    # Configuration
    is_required = fields.Boolean(
        string='Required Section',
        default=True,
        help='Section must be completed'
    )
    
    is_repeatable = fields.Boolean(
        string='Repeatable',
        default=False,
        help='Section can be filled multiple times (for rooms, assets)'
    )
    
    # Skip Logic
    condition_ids = fields.One2many(
        'property_fielder.condition.trigger',
        'target_section_id',
        string='Skip Conditions',
        help='Conditions that show/hide this section'
    )
    
    # Icon for mobile UI
    icon = fields.Char(
        string='Icon',
        default='fa-clipboard-list',
        help='FontAwesome icon for mobile display'
    )
    
    # Color for visual grouping
    color = fields.Integer(
        string='Color Index',
        default=0,
        help='Color index for kanban display'
    )
    
    # Statistics
    item_count = fields.Integer(
        string='Item Count',
        compute='_compute_item_count',
        store=True,
        help='Number of items in this section'
    )
    
    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)
    
    # Display name with template context
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.template_id:
                name = '%s / %s' % (record.template_id.name, record.name)
            result.append((record.id, name))
        return result
    
    # Action to add new item
    def action_add_item(self):
        """Open wizard to add new item to section."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Add Item'),
            'res_model': 'property_fielder.inspection.template.item',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_section_id': self.id,
                'default_sequence': (max(self.item_ids.mapped('sequence') or [0]) + 10),
            },
        }

