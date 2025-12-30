# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Inspection(models.Model):
    """Inspection - A template-based data collection linked to a job"""
    
    _name = 'property_fielder.inspection'
    _description = 'Inspection'
    _inherits = {'property_fielder.job': 'job_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Link to Job (delegation inheritance)
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        required=True,
        ondelete='cascade',
        help='Underlying job record'
    )
    
    # Template
    template_id = fields.Many2one(
        'property_fielder.inspection.template',
        string='Template',
        required=True,
        tracking=True,
        help='Inspection template to use'
    )
    
    # Property link (related from job)
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        tracking=True,
        help='Property being inspected'
    )
    
    # Responses
    response_ids = fields.One2many(
        'property_fielder.inspection.response',
        'inspection_id',
        string='Responses',
        help='Responses to template items'
    )
    
    # Asset Responses (for CP12/EICR)
    asset_response_ids = fields.One2many(
        'property_fielder.inspection.asset.response',
        'inspection_id',
        string='Asset Responses',
        help='Asset-level responses'
    )
    
    # Overall Result
    overall_result = fields.Selection([
        ('pending', 'Pending'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('incomplete', 'Incomplete'),
    ], string='Overall Result', default='pending', tracking=True)
    
    # Completion
    completion_date = fields.Datetime(
        string='Completion Date',
        readonly=True,
        tracking=True,
        help='Date/time inspection was completed'
    )
    
    completion_percentage = fields.Float(
        string='Completion %',
        compute='_compute_completion',
        store=True,
        help='Percentage of required items completed'
    )
    
    # Inspector license snapshot (for certifications)
    inspector_license_number = fields.Char(
        string='Inspector License Number',
        help='Gas Safe / NICEIC ID captured at inspection time'
    )
    
    inspector_license_expiry = fields.Date(
        string='License Expiry at Inspection',
        help='License expiry date at time of inspection'
    )
    
    # Additional photos (not tied to template items)
    extra_photo_ids = fields.Many2many(
        'ir.attachment',
        'inspection_extra_photo_rel',
        'inspection_id',
        'attachment_id',
        string='Additional Photos',
        help='Photos taken outside of template questions'
    )
    
    # Signatures (stored as binary for independence from mobile addon)
    inspector_signature = fields.Binary(
        string='Inspector Signature',
        attachment=True,
        help='Inspector signature image'
    )

    inspector_signature_name = fields.Char(
        string='Inspector Signer Name',
        help='Name of inspector who signed'
    )

    inspector_signature_date = fields.Datetime(
        string='Inspector Signed Date',
        help='When inspector signed'
    )

    tenant_signature = fields.Binary(
        string='Tenant Signature',
        attachment=True,
        help='Tenant/resident signature image'
    )

    tenant_signature_name = fields.Char(
        string='Tenant Signer Name',
        help='Name of tenant who signed'
    )

    tenant_signature_date = fields.Datetime(
        string='Tenant Signed Date',
        help='When tenant signed'
    )
    
    # Statistics
    response_count = fields.Integer(
        string='Responses',
        compute='_compute_response_count',
        store=True,
    )
    
    defect_count = fields.Integer(
        string='Defects Found',
        compute='_compute_defect_count',
        help='Number of defects identified'
    )
    
    # Report
    report_template_id = fields.Many2one(
        'ir.actions.report',
        string='Report Template',
        help='QWeb report template for certificate generation'
    )
    
    @api.depends('response_ids')
    def _compute_response_count(self):
        for record in self:
            record.response_count = len(record.response_ids)
    
    @api.depends('response_ids', 'template_id.section_ids.item_ids')
    def _compute_completion(self):
        for record in self:
            if not record.template_id:
                record.completion_percentage = 0.0
                continue
            
            required_items = record.template_id.section_ids.item_ids.filtered(
                lambda i: i.is_required
            )
            if not required_items:
                record.completion_percentage = 100.0
                continue
            
            answered = record.response_ids.filtered(
                lambda r: r.item_id in required_items and r.is_answered
            )
            record.completion_percentage = (len(answered) / len(required_items)) * 100

    def _compute_defect_count(self):
        """Compute defect count - overridden by defects addon."""
        for record in self:
            record.defect_count = record.response_ids.filtered(
                lambda r: r.creates_defect
            ).__len__()

    # ============================================================
    # CRUD OVERRIDES
    # ============================================================

    @api.model_create_multi
    def create(self, vals_list):
        """Snapshot inspector license at creation."""
        records = super().create(vals_list)
        for record in records:
            if record.inspector_id:
                # Snapshot gas safe license if available
                if hasattr(record.inspector_id, 'gas_safe_number'):
                    record.inspector_license_number = record.inspector_id.gas_safe_number
                    record.inspector_license_expiry = record.inspector_id.gas_safe_expiry
        return records

    # ============================================================
    # ACTIONS
    # ============================================================

    def action_initialize_responses(self):
        """Create empty response records for all template items."""
        self.ensure_one()
        Response = self.env['property_fielder.inspection.response']

        for section in self.template_id.section_ids:
            for item in section.item_ids:
                existing = self.response_ids.filtered(lambda r: r.item_id == item)
                if not existing:
                    Response.create({
                        'inspection_id': self.id,
                        'item_id': item.id,
                    })

        return True

    def action_prefill_from_previous(self):
        """Pre-fill responses from previous inspection."""
        self.ensure_one()

        for response in self.response_ids:
            if response.item_id.load_previous_value:
                prev = self._get_previous_response(response.item_id)
                if prev:
                    response.write({
                        'response_text': prev.response_text,
                        'response_numeric': prev.response_numeric,
                        'response_option_id': prev.response_option_id.id if prev.response_option_id else False,
                        'response_date': prev.response_date,
                    })

        return True

    def _get_previous_response(self, item):
        """Load answer from most recent 'done' inspection of same template on same property."""
        previous_inspection = self.search([
            ('template_id', '=', self.template_id.id),
            ('property_id', '=', self.property_id.id),
            ('overall_result', '!=', 'pending'),
            ('id', '!=', self.id),
        ], order='completion_date desc', limit=1)

        if previous_inspection:
            previous_response = previous_inspection.response_ids.filtered(
                lambda r: r.item_id.code == item.code
            )
            if previous_response:
                return previous_response[0]
        return False

    def action_complete(self):
        """Mark inspection as complete and calculate result."""
        self.ensure_one()

        # Check completion
        if self.completion_percentage < 100:
            raise ValidationError(_("All required items must be answered."))

        # Check signatures if required
        if self.template_id.requires_signature and not self.tenant_signature_id:
            raise ValidationError(_("Tenant signature is required."))

        # Calculate overall result
        failed_responses = self.response_ids.filtered(lambda r: r.creates_defect)
        if failed_responses:
            self.overall_result = 'fail'
        else:
            self.overall_result = 'pass'

        self.completion_date = fields.Datetime.now()

        # Update job state
        self.job_id.state = 'completed'

        return True

    def action_view_responses(self):
        """View all responses for this inspection."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Responses'),
            'res_model': 'property_fielder.inspection.response',
            'view_mode': 'tree,form',
            'domain': [('inspection_id', '=', self.id)],
            'context': {'default_inspection_id': self.id},
        }

