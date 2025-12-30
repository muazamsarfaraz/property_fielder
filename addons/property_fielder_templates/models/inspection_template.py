# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InspectionTemplate(models.Model):
    """Inspection Template Definition"""
    
    _name = 'property_fielder.inspection.template'
    _description = 'Inspection Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Basic Information
    name = fields.Char(
        string='Template Name',
        required=True,
        tracking=True,
        help='Name of the inspection template'
    )
    
    code = fields.Char(
        string='Template Code',
        required=True,
        copy=False,
        help='Unique code for the template'
    )
    
    description = fields.Text(
        string='Description',
        help='Description of the template and its purpose'
    )
    
    # Linked Certification Type (from property_management)
    certification_type_id = fields.Many2one(
        'property_fielder.certification.type',
        string='Certification Type',
        tracking=True,
        help='Linked certification type for automatic certificate creation'
    )
    
    # Versioning
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True,
        help='Template version number'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Sections
    section_ids = fields.One2many(
        'property_fielder.inspection.template.section',
        'template_id',
        string='Sections',
        copy=True,
        help='Sections in this template'
    )
    
    # Configuration
    estimated_duration = fields.Integer(
        string='Estimated Duration (minutes)',
        default=60,
        help='Expected time to complete the inspection'
    )
    
    requires_signature = fields.Boolean(
        string='Requires Signature',
        default=False,
        help='Tenant/resident signature is required'
    )
    
    requires_photos = fields.Boolean(
        string='Requires Photos',
        default=False,
        help='At least one photo is required'
    )
    
    min_photos = fields.Integer(
        string='Minimum Photos',
        default=0,
        help='Minimum number of photos required'
    )

    is_asset_based = fields.Boolean(
        string='Asset-Based Template',
        default=False,
        help='Template is for asset-based inspections (e.g., CP12, EICR) where items are repeated per asset'
    )

    # Statistics
    item_count = fields.Integer(
        string='Item Count',
        compute='_compute_item_count',
        store=True,
        help='Number of items in the template'
    )
    
    section_count = fields.Integer(
        string='Section Count',
        compute='_compute_section_count',
        store=True,
        help='Number of sections in the template'
    )
    
    inspection_count = fields.Integer(
        string='Inspections',
        compute='_compute_inspection_count',
        help='Number of inspections using this template'
    )
    
    # Calculations
    calculation_ids = fields.One2many(
        'property_fielder.template.calculation',
        'template_id',
        string='Calculations',
        help='Calculation rules for this template'
    )
    
    # Report Template
    report_template_id = fields.Many2one(
        'ir.actions.report',
        string='Report Template',
        help='QWeb report template for certificate generation'
    )
    
    @api.depends('section_ids')
    def _compute_section_count(self):
        for record in self:
            record.section_count = len(record.section_ids)
    
    @api.depends('section_ids.item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = sum(len(section.item_ids) for section in record.section_ids)
    
    def _compute_inspection_count(self):
        Inspection = self.env['property_fielder.inspection']
        for record in self:
            record.inspection_count = Inspection.search_count([
                ('template_id', '=', record.id)
            ])
    
    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(_("Template code must be unique."))

    # ============================================================
    # ACTIONS
    # ============================================================

    def action_activate(self):
        """Activate the template for use."""
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only draft templates can be activated."))
            if not record.section_ids:
                raise ValidationError(_("Template must have at least one section."))
            record.state = 'active'

    def action_archive(self):
        """Archive the template (no longer available for new inspections)."""
        for record in self:
            record.state = 'archived'

    def action_new_version(self):
        """Create a new version of this template."""
        self.ensure_one()
        new_template = self.copy({
            'name': _("%s (v%d)") % (self.name, self.version + 1),
            'code': '%s_v%d' % (self.code, self.version + 1),
            'version': self.version + 1,
            'state': 'draft',
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Template Version'),
            'res_model': 'property_fielder.inspection.template',
            'res_id': new_template.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_inspections(self):
        """View inspections using this template."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspections'),
            'res_model': 'property_fielder.inspection',
            'view_mode': 'tree,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }

    def action_preview(self):
        """Preview the template in mobile-like view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Template Preview'),
            'res_model': 'property_fielder.inspection.template',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'preview_mode': True},
        }

