# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MatrixSchema(models.Model):
    """Matrix Question Schema - Defines rows and columns for matrix response type"""
    
    _name = 'property_fielder.matrix.schema'
    _description = 'Matrix Question Schema'
    _order = 'name'
    
    name = fields.Char(
        string='Schema Name',
        required=True,
        help='Name of this matrix schema'
    )
    
    # Link to template item (optional - can be reusable)
    item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Template Item',
        ondelete='cascade',
        help='Template item using this schema'
    )
    
    # Rows and Columns
    row_ids = fields.One2many(
        'property_fielder.matrix.row',
        'schema_id',
        string='Rows',
        copy=True,
        help='Row definitions'
    )
    
    column_ids = fields.One2many(
        'property_fielder.matrix.column',
        'schema_id',
        string='Columns',
        copy=True,
        help='Column definitions'
    )
    
    # Description
    description = fields.Text(
        string='Description',
        help='Description of this matrix'
    )


class MatrixRow(models.Model):
    """Matrix Row Definition"""
    
    _name = 'property_fielder.matrix.row'
    _description = 'Matrix Row Definition'
    _order = 'sequence, id'
    
    # Parent Schema
    schema_id = fields.Many2one(
        'property_fielder.matrix.schema',
        string='Schema',
        required=True,
        ondelete='cascade'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    
    label = fields.Char(
        string='Label',
        required=True,
        translate=True,
        help='Row label'
    )
    
    code = fields.Char(
        string='Code',
        help='Internal code for reporting'
    )


class MatrixColumn(models.Model):
    """Matrix Column Definition"""
    
    _name = 'property_fielder.matrix.column'
    _description = 'Matrix Column Definition'
    _order = 'sequence, id'
    
    # Parent Schema
    schema_id = fields.Many2one(
        'property_fielder.matrix.schema',
        string='Schema',
        required=True,
        ondelete='cascade'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    
    label = fields.Char(
        string='Label',
        required=True,
        translate=True,
        help='Column label'
    )
    
    code = fields.Char(
        string='Code',
        help='Internal code for reporting'
    )
    
    column_type = fields.Selection([
        ('radio', 'Radio (single select)'),
        ('checkbox', 'Checkbox (multi-select)'),
        ('text', 'Text input'),
        ('numeric', 'Numeric input'),
    ], string='Column Type', default='radio')
    
    # Options for radio/checkbox columns
    options = fields.Char(
        string='Options',
        help='Comma-separated options (e.g., Good,Fair,Poor)'
    )

