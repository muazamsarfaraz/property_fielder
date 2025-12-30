# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InspectionResponse(models.Model):
    """Inspector's answer to a template item"""
    
    _name = 'property_fielder.inspection.response'
    _description = 'Inspection Response'
    _order = 'item_sequence, id'
    
    # Parent Inspection
    inspection_id = fields.Many2one(
        'property_fielder.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade',
        help='Parent inspection'
    )
    
    # Template Item
    item_id = fields.Many2one(
        'property_fielder.inspection.template.item',
        string='Template Item',
        required=True,
        ondelete='restrict',
        help='Template item being answered'
    )
    
    # For ordering (related from item)
    item_sequence = fields.Integer(
        string='Item Sequence',
        related='item_id.sequence',
        store=True,
    )
    
    # Asset Response link (for CP12/EICR)
    asset_response_id = fields.Many2one(
        'property_fielder.inspection.asset.response',
        string='Asset Response',
        ondelete='cascade',
        help='Parent asset response for asset-level items'
    )
    
    # ============================================================
    # RESPONSE VALUES (different types stored in different fields)
    # ============================================================
    
    # Text/Yes-No/Pass-Fail response
    response_text = fields.Text(
        string='Text Response',
        help='Text or selection value'
    )
    
    # Numeric response
    response_numeric = fields.Float(
        string='Numeric Response',
        help='Numeric value'
    )
    
    # Single option selection
    response_option_id = fields.Many2one(
        'property_fielder.inspection.template.item.option',
        string='Selected Option',
        help='Selected option for single choice'
    )
    
    # Multiple option selection
    response_option_ids = fields.Many2many(
        'property_fielder.inspection.template.item.option',
        'inspection_response_option_rel',
        'response_id',
        'option_id',
        string='Selected Options',
        help='Selected options for multiple choice'
    )
    
    # Date response
    response_date = fields.Date(
        string='Date Response',
        help='Date value'
    )
    
    # JSON response (for tabular/matrix)
    response_json = fields.Json(
        string='Structured Response',
        help='JSON data for tabular/matrix responses'
    )
    
    # ============================================================
    # ATTACHMENTS
    # ============================================================
    
    # Photos
    photo_ids = fields.Many2many(
        'ir.attachment',
        'inspection_response_photo_rel',
        'response_id',
        'attachment_id',
        string='Photos',
        help='Photo attachments'
    )
    
    # Signature
    signature_id = fields.Many2one(
        'property_fielder.job.signature',
        string='Signature',
        help='Signature for this item'
    )
    
    # ============================================================
    # FLAGS
    # ============================================================
    
    is_answered = fields.Boolean(
        string='Answered',
        compute='_compute_is_answered',
        store=True,
        help='Whether the item has been answered'
    )
    
    creates_defect = fields.Boolean(
        string='Creates Defect',
        compute='_compute_creates_defect',
        store=True,
        help='Whether this response triggers defect creation'
    )
    
    # Notes
    notes = fields.Text(
        string='Notes',
        help='Additional notes for this response'
    )
    
    @api.depends('response_text', 'response_numeric', 'response_option_id', 
                 'response_option_ids', 'response_date', 'response_json', 'photo_ids')
    def _compute_is_answered(self):
        for record in self:
            record.is_answered = bool(
                record.response_text or
                record.response_numeric or
                record.response_option_id or
                record.response_option_ids or
                record.response_date or
                record.response_json or
                record.photo_ids
            )
    
    @api.depends('response_text', 'response_option_id', 'item_id.creates_defect')
    def _compute_creates_defect(self):
        for record in self:
            creates = False
            if record.item_id.creates_defect:
                # Check for failure responses
                if record.response_option_id and record.response_option_id.is_failure:
                    creates = True
                elif record.response_text in ('no', 'fail', 'id', 'ar', 'c1', 'c2'):
                    creates = True
            record.creates_defect = creates

