# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TemplateItem(models.Model):
    """Template Item - Individual question or check"""
    
    _name = 'property_fielder.inspection.template.item'
    _description = 'Template Item'
    _order = 'sequence, id'
    
    # Parent Section
    section_id = fields.Many2one(
        'property_fielder.inspection.template.section',
        string='Section',
        required=True,
        ondelete='cascade',
        help='Parent section'
    )
    
    # Template (related for filtering)
    template_id = fields.Many2one(
        'property_fielder.inspection.template',
        string='Template',
        related='section_id.template_id',
        store=True,
        readonly=True,
    )
    
    # Basic Information
    code = fields.Char(
        string='Item Code',
        help='Unique code for reference'
    )
    
    question = fields.Char(
        string='Question',
        required=True,
        help='Question text'
    )
    
    help_text = fields.Text(
        string='Help Text',
        help='Guidance for the inspector'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    
    # Response Type
    response_type = fields.Selection([
        ('yes_no', 'Yes/No'),
        ('pass_fail', 'Pass/Fail/N/A'),
        ('gas_severity', 'Gas Severity (ID/AR/NCS)'),
        ('electrical_code', 'Electrical Code (C1/C2/C3/FI)'),
        ('hhsrs_severity', 'HHSRS Severity (1-4)'),
        ('numeric', 'Numeric'),
        ('text', 'Text'),
        ('photo', 'Photo'),
        ('select_one', 'Single Choice'),
        ('select_multi', 'Multiple Choice'),
        ('date', 'Date'),
        ('signature', 'Signature'),
        ('reading', 'Meter Reading'),
        ('tabular', 'Table Grid'),
        ('matrix', 'Question Matrix'),
        ('asset_list', 'Asset List (CP12/EICR)'),
    ], string='Response Type', default='yes_no', required=True)
    
    # Options (for select_one/select_multi)
    option_ids = fields.One2many(
        'property_fielder.inspection.template.item.option',
        'item_id',
        string='Options',
        copy=True,
        help='Options for choice fields'
    )
    
    # Validation
    is_required = fields.Boolean(
        string='Required',
        default=True,
        help='Must answer this question'
    )
    
    # Defect Creation
    creates_defect = fields.Boolean(
        string='Creates Defect',
        default=False,
        help='Failure response creates a defect'
    )
    
    defect_severity = fields.Selection([
        # Gas severity codes
        ('id', 'ID - Immediately Dangerous'),
        ('ar', 'AR - At Risk'),
        ('ncs', 'NCS - Not to Current Standard'),
        # Electrical severity codes
        ('c1', 'C1 - Danger Present'),
        ('c2', 'C2 - Potentially Dangerous'),
        ('c3', 'C3 - Improvement Recommended'),
        ('fi', 'FI - Further Investigation'),
        # General categories
        ('cat1', 'Category 1 (24 hours)'),
        ('cat2', 'Category 2 (28 days)'),
    ], string='Defect Severity', help='Severity when defect is created')
    
    # Fault code reference (string to avoid layer violation)
    fault_code_reference = fields.Char(
        string='Fault Code Reference',
        help='Reference to fault code (from defects addon)'
    )
    
    # Photo Requirements
    photo_required = fields.Boolean(
        string='Photo Required',
        default=False,
        help='Photo must be taken for this item'
    )
    
    photo_min_count = fields.Integer(
        string='Minimum Photos',
        default=1,
        help='Minimum number of photos required'
    )

    # Numeric/Reading Validation
    unit_of_measure = fields.Char(
        string='Unit of Measure',
        help='Unit for numeric/reading values (e.g., mbar, V, A)'
    )

    min_value = fields.Float(
        string='Minimum Value',
        help='Minimum acceptable value for numeric responses'
    )

    max_value = fields.Float(
        string='Maximum Value',
        help='Maximum acceptable value for numeric responses'
    )

    default_value = fields.Char(
        string='Default Value',
        help='Default value to pre-fill for this item'
    )

    # Skip Logic
    condition_ids = fields.One2many(
        'property_fielder.condition.trigger',
        'target_item_id',
        string='Skip Conditions',
        help='Conditions that show/hide this item'
    )
    
    # Validation Rules
    validation_rule_ids = fields.One2many(
        'property_fielder.validation.rule',
        'item_id',
        string='Validation Rules',
        help='Conditional validation rules'
    )
    
    # Pre-fill from previous inspection
    load_previous_value = fields.Boolean(
        string='Load Previous Value',
        default=False,
        help='Pre-fill with value from previous inspection'
    )
    
    # Scoring weight for aggregations
    weight = fields.Integer(
        string='Weight',
        default=1,
        help='Scoring weight for calculations'
    )

    # Numeric validation
    min_value = fields.Float(
        string='Minimum Value',
        help='Minimum value for numeric responses'
    )

    max_value = fields.Float(
        string='Maximum Value',
        help='Maximum value for numeric responses'
    )

    unit = fields.Char(
        string='Unit',
        help='Unit for numeric/reading responses (e.g., kWh, mBar)'
    )

    # Matrix schema link (for matrix response type)
    matrix_schema_id = fields.Many2one(
        'property_fielder.matrix.schema',
        string='Matrix Schema',
        help='Schema definition for matrix response type'
    )

    # Display name
    def name_get(self):
        result = []
        for record in self:
            name = record.question
            if record.code:
                name = '[%s] %s' % (record.code, record.question)
            result.append((record.id, name))
        return result

