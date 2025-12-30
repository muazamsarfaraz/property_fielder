# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ValidationRule(models.Model):
    """Conditional Validation Rules"""
    
    _name = 'property_fielder.validation.rule'
    _description = 'Validation Rule'
    _order = 'id'
    
    # The item this validation applies to
    item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Item',
        required=True,
        ondelete='cascade',
        help='Item this validation applies to'
    )
    
    # Trigger item (the item whose answer triggers validation)
    trigger_item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Trigger Item',
        ondelete='cascade',
        help='Item whose answer triggers this validation'
    )
    
    # Trigger condition
    trigger_operator = fields.Selection([
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
    ], string='Trigger Operator', default='equals')
    
    trigger_value = fields.Char(
        string='Trigger Value',
        help='Value that triggers the validation'
    )
    
    # Validation type
    validation_type = fields.Selection([
        ('required', 'Make Required'),
        ('photo_required', 'Require Photo'),
        ('min_value', 'Minimum Value'),
        ('max_value', 'Maximum Value'),
        ('regex', 'Pattern Match'),
        ('min_length', 'Minimum Length'),
        ('max_length', 'Maximum Length'),
    ], string='Validation Type', default='required', required=True)
    
    validation_value = fields.Char(
        string='Validation Value',
        help='Value for the validation (min/max number, pattern, etc.)'
    )
    
    # Error message
    error_message = fields.Char(
        string='Error Message',
        translate=True,
        help='Custom error message to display'
    )
    
    def check_validation(self, trigger_response_value, target_response_value):
        """Check if validation passes."""
        self.ensure_one()
        
        # First check if trigger condition is met
        if self.trigger_item_id:
            trigger_met = False
            if self.trigger_operator == 'equals':
                trigger_met = str(trigger_response_value) == str(self.trigger_value)
            elif self.trigger_operator == 'not_equals':
                trigger_met = str(trigger_response_value) != str(self.trigger_value)
            
            if not trigger_met:
                return True  # Validation doesn't apply
        
        # Check validation
        if self.validation_type == 'required':
            if not target_response_value:
                return False
        elif self.validation_type == 'photo_required':
            # Check handled at response level
            pass
        elif self.validation_type == 'min_value':
            try:
                if float(target_response_value or 0) < float(self.validation_value or 0):
                    return False
            except (ValueError, TypeError):
                return False
        elif self.validation_type == 'max_value':
            try:
                if float(target_response_value or 0) > float(self.validation_value or 0):
                    return False
            except (ValueError, TypeError):
                return False
        elif self.validation_type == 'min_length':
            if len(str(target_response_value or '')) < int(self.validation_value or 0):
                return False
        elif self.validation_type == 'max_length':
            if len(str(target_response_value or '')) > int(self.validation_value or 0):
                return False
        elif self.validation_type == 'regex':
            import re
            try:
                if not re.match(self.validation_value or '', str(target_response_value or '')):
                    return False
            except re.error:
                return False
        
        return True
    
    # Display name
    def name_get(self):
        result = []
        for record in self:
            name = _("%s: %s") % (record.validation_type, record.validation_value or '')
            if record.trigger_item_id:
                name = _("If %s %s %s → %s") % (
                    record.trigger_item_id.question,
                    record.trigger_operator,
                    record.trigger_value,
                    name
                )
            result.append((record.id, name))
        return result

