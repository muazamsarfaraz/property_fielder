# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConditionTrigger(models.Model):
    """Skip Logic Rules - Conditions for showing/hiding sections and items"""
    
    _name = 'property_fielder.condition.trigger'
    _description = 'Condition Trigger'
    _order = 'id'
    
    # Source Item (the question whose answer triggers the condition)
    source_item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Source Item',
        required=True,
        ondelete='cascade',
        help='Item whose answer triggers this condition'
    )
    
    # Source Template (for filtering)
    template_id = fields.Many2one(
        'property_fielder.inspection.template',
        string='Template',
        related='source_item_id.template_id',
        store=True,
        readonly=True,
    )
    
    # Condition
    operator = fields.Selection([
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('greater', 'Greater Than'),
        ('less', 'Less Than'),
        ('contains', 'Contains'),
        ('is_empty', 'Is Empty'),
        ('is_not_empty', 'Is Not Empty'),
    ], string='Operator', default='equals', required=True)
    
    value = fields.Char(
        string='Value',
        help='Value to compare against'
    )
    
    # Target Section (mutually exclusive with target item)
    target_section_id = fields.Many2one(
        'property_fielder.inspection.template.section',
        string='Target Section',
        ondelete='cascade',
        help='Section affected by this condition'
    )
    
    # Target Item (mutually exclusive with target section)
    target_item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Target Item',
        ondelete='cascade',
        help='Item affected by this condition'
    )
    
    # Action
    action = fields.Selection([
        ('show', 'Show'),
        ('hide', 'Hide'),
        ('require', 'Make Required'),
        ('optional', 'Make Optional'),
    ], string='Action', default='show', required=True)
    
    # Logic combination (for multiple conditions)
    logic = fields.Selection([
        ('and', 'AND'),
        ('or', 'OR'),
    ], string='Logic', default='and', help='How to combine with other conditions')
    
    @api.constrains('target_section_id', 'target_item_id')
    def _check_target(self):
        for record in self:
            if not record.target_section_id and not record.target_item_id:
                raise ValidationError(_("Either target section or target item must be set."))
            if record.target_section_id and record.target_item_id:
                raise ValidationError(_("Cannot set both target section and target item."))
    
    def evaluate(self, response_value):
        """Evaluate if condition is met based on response value."""
        self.ensure_one()
        
        if self.operator == 'equals':
            return str(response_value) == str(self.value)
        elif self.operator == 'not_equals':
            return str(response_value) != str(self.value)
        elif self.operator == 'greater':
            try:
                return float(response_value) > float(self.value)
            except (ValueError, TypeError):
                return False
        elif self.operator == 'less':
            try:
                return float(response_value) < float(self.value)
            except (ValueError, TypeError):
                return False
        elif self.operator == 'contains':
            return str(self.value) in str(response_value)
        elif self.operator == 'is_empty':
            return not response_value
        elif self.operator == 'is_not_empty':
            return bool(response_value)
        
        return False
    
    # Display name
    def name_get(self):
        result = []
        for record in self:
            source = record.source_item_id.question or 'Unknown'
            target = record.target_section_id.name or record.target_item_id.question or 'Unknown'
            name = _("If %s %s %s → %s %s") % (
                source,
                record.operator,
                record.value or '',
                record.action,
                target
            )
            result.append((record.id, name))
        return result

