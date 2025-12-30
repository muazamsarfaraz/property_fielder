# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class TemplateCalculation(models.Model):
    """Template Calculation Rule - Computes values from inspection responses"""
    
    _name = 'property_fielder.template.calculation'
    _description = 'Template Calculation'
    _order = 'sequence, id'
    
    # Parent Template
    template_id = fields.Many2one(
        'property_fielder.inspection.template',
        string='Template',
        required=True,
        ondelete='cascade',
        help='Parent template'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    
    name = fields.Char(
        string='Calculation Name',
        required=True,
        help='e.g., Total Score, Compliance %'
    )
    
    code = fields.Char(
        string='Code',
        help='Code for referencing in reports'
    )
    
    # Formula
    formula = fields.Text(
        string='Formula',
        required=True,
        help='Python expression. Available: responses, sum(), count(), avg(), len()'
    )
    
    # Result type
    result_type = fields.Selection([
        ('numeric', 'Numeric'),
        ('percentage', 'Percentage'),
        ('grade', 'Grade (A-F)'),
        ('pass_fail', 'Pass/Fail'),
        ('text', 'Text'),
    ], string='Result Type', default='numeric', required=True)
    
    # Display options
    display_in_report = fields.Boolean(
        string='Display in Report',
        default=True,
        help='Show in generated report/certificate'
    )
    
    display_label = fields.Char(
        string='Display Label',
        translate=True,
        help='Label to show in report (if different from name)'
    )
    
    # Help text
    description = fields.Text(
        string='Description',
        help='Description of what this calculates'
    )
    
    def compute_result(self, inspection):
        """Evaluate formula against inspection responses."""
        self.ensure_one()
        
        # Build responses dict: item_code → response_value
        responses = {}
        scores = []
        
        for r in inspection.response_ids:
            code = r.item_id.code or str(r.item_id.id)
            
            # Get the response value based on type
            if r.response_numeric:
                responses[code] = r.response_numeric
                scores.append(r.response_numeric)
            elif r.response_option_id:
                responses[code] = r.response_option_id.value
                if r.response_option_id.score:
                    scores.append(r.response_option_id.score)
            elif r.response_text:
                responses[code] = r.response_text
            elif r.response_date:
                responses[code] = r.response_date
            else:
                responses[code] = None
        
        # Helper functions for formulas
        def count_value(val):
            return sum(1 for v in responses.values() if v == val)
        
        def count_not_empty():
            return sum(1 for v in responses.values() if v is not None)
        
        def avg(items):
            if not items:
                return 0
            return sum(items) / len(items)
        
        # Safe evaluation context
        eval_context = {
            'responses': responses,
            'scores': scores,
            'sum': sum,
            'len': len,
            'avg': avg,
            'count_value': count_value,
            'count_not_empty': count_not_empty,
            'min': min,
            'max': max,
            'round': round,
        }
        
        try:
            result = safe_eval(self.formula, eval_context)
        except Exception as e:
            _logger.error("Error evaluating formula %s: %s", self.formula, str(e))
            return None
        
        # Format result based on type
        if self.result_type == 'percentage':
            result = round(float(result or 0), 1)
        elif self.result_type == 'grade':
            # Convert numeric to grade
            score = float(result or 0)
            if score >= 90:
                result = 'A'
            elif score >= 80:
                result = 'B'
            elif score >= 70:
                result = 'C'
            elif score >= 60:
                result = 'D'
            elif score >= 50:
                result = 'E'
            else:
                result = 'F'
        elif self.result_type == 'pass_fail':
            result = 'Pass' if result else 'Fail'
        
        return result

