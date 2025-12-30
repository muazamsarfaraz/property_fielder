# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PropertyInspection(models.Model):
    _name = 'property_fielder.property.inspection'
    _description = 'Property Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, id desc'

    name = fields.Char(
        string='Inspection Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    # Property & Type
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    certification_type_id = fields.Many2one(
        'property_fielder.certification.type',
        string='Certification Type',
        required=True,
        tracking=True
    )
    
    flage_category = fields.Selection(
        related='certification_type_id.flage_category',
        string='FLAGE+ Category',
        store=True
    )

    # Property Access Information (related from property for inspector reference)
    property_key_safe_location = fields.Char(
        related='property_id.key_safe_location',
        string='Key Safe Location',
        readonly=True
    )
    property_key_safe_code = fields.Char(
        related='property_id.key_safe_code',
        string='Key Safe Code',
        readonly=True,
        groups='property_fielder_property_management.group_property_manager'
    )
    property_entry_instructions = fields.Text(
        related='property_id.entry_instructions',
        string='Entry Instructions',
        readonly=True
    )
    property_parking_instructions = fields.Text(
        related='property_id.parking_instructions',
        string='Parking Instructions',
        readonly=True
    )
    property_access_contact_id = fields.Many2one(
        related='property_id.access_contact_id',
        string='Access Contact',
        readonly=True
    )
    property_access_contact_phone = fields.Char(
        related='property_id.access_contact_phone',
        string='Access Contact Phone',
        readonly=True
    )
    property_access_hours = fields.Char(
        related='property_id.access_hours',
        string='Access Hours',
        readonly=True
    )
    property_access_notes = fields.Text(
        related='property_id.access_notes',
        string='Access Notes',
        readonly=True
    )
    property_address = fields.Char(
        related='property_id.full_address',
        string='Property Address',
        readonly=True
    )

    # Scheduling
    scheduled_date = fields.Date(
        string='Scheduled Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    completed_date = fields.Date(string='Completed Date', tracking=True)
    
    # Inspector
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        tracking=True
    )
    
    # Integration with Field Service
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Field Service Job',
        ondelete='set null',
        help='Linked field service job for this inspection'
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Results
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional Pass')
    ], string='Result', tracking=True)
    
    findings = fields.Text(string='Findings')
    recommendations = fields.Text(string='Recommendations')
    
    # Certification
    certification_id = fields.Many2one(
        'property_fielder.property.certification',
        string='Generated Certificate',
        ondelete='set null',
        readonly=True
    )
    
    # Documents
    report_file = fields.Binary(string='Inspection Report', attachment=True)
    report_filename = fields.Char(string='Report Filename')

    # Legacy simple photo attachments
    photo_ids = fields.Many2many(
        'ir.attachment',
        string='Quick Photos',
        help='Quick photos taken during inspection (legacy)'
    )

    # Structured Inspection Photos
    inspection_photo_ids = fields.One2many(
        'property_fielder.inspection.photo',
        'inspection_id',
        string='Inspection Photos',
        help='Structured inspection photos with categories and annotations'
    )
    photo_count = fields.Integer(
        string='Photo Count',
        compute='_compute_photo_count'
    )

    # Checklist
    checklist_item_ids = fields.One2many(
        'property_fielder.inspection.checklist.item',
        'inspection_id',
        string='Checklist Items'
    )
    checklist_count = fields.Integer(
        string='Checklist Items',
        compute='_compute_checklist_stats'
    )
    checklist_completed = fields.Integer(
        string='Completed Items',
        compute='_compute_checklist_stats'
    )
    checklist_passed = fields.Integer(
        string='Passed Items',
        compute='_compute_checklist_stats'
    )
    checklist_failed = fields.Integer(
        string='Failed Items',
        compute='_compute_checklist_stats'
    )
    checklist_progress = fields.Float(
        string='Checklist Progress (%)',
        compute='_compute_checklist_stats'
    )

    # Signatures
    inspector_signature = fields.Image(
        string='Inspector Signature',
        max_width=500,
        max_height=200,
        help='Digital signature of the inspector'
    )
    inspector_signature_date = fields.Datetime(
        string='Inspector Signed Date'
    )
    inspector_signature_name = fields.Char(
        string='Inspector Printed Name'
    )

    witness_signature = fields.Image(
        string='Witness/Tenant Signature',
        max_width=500,
        max_height=200,
        help='Digital signature of witness, tenant, or property owner'
    )
    witness_signature_date = fields.Datetime(
        string='Witness Signed Date'
    )
    witness_signature_name = fields.Char(
        string='Witness Printed Name'
    )
    witness_signature_role = fields.Selection([
        ('tenant', 'Tenant'),
        ('owner', 'Property Owner'),
        ('agent', 'Managing Agent'),
        ('contractor', 'Contractor'),
        ('other', 'Other')
    ], string='Witness Role')

    is_witnessed = fields.Boolean(
        string='Witnessed Inspection',
        default=False,
        help='Check if this inspection was witnessed by tenant/owner'
    )

    # Notes
    notes = fields.Text(string='Notes')

    # Constraints (Odoo 19 style)
    _check_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Inspection number must be unique!',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('property_fielder.property.inspection') or _('New')
        return super(PropertyInspection, self).create(vals_list)

    @api.depends('inspection_photo_ids')
    def _compute_photo_count(self):
        for inspection in self:
            inspection.photo_count = len(inspection.inspection_photo_ids)

    @api.depends('checklist_item_ids', 'checklist_item_ids.result')
    def _compute_checklist_stats(self):
        for inspection in self:
            items = inspection.checklist_item_ids
            total = len(items)
            completed = len(items.filtered(lambda i: i.result != 'pending'))
            passed = len(items.filtered(lambda i: i.result == 'pass'))
            failed = len(items.filtered(lambda i: i.result == 'fail'))

            inspection.checklist_count = total
            inspection.checklist_completed = completed
            inspection.checklist_passed = passed
            inspection.checklist_failed = failed
            inspection.checklist_progress = (completed / total * 100) if total else 0

    def action_load_checklist(self):
        """Load checklist items from the certification type's template."""
        self.ensure_one()
        if not self.certification_type_id:
            raise ValidationError(_('Please select a certification type first.'))

        # Find template for this certification type
        template = self.env['property_fielder.checklist.template'].search([
            ('certification_type_id', '=', self.certification_type_id.id),
            ('active', '=', True)
        ], limit=1)

        if not template:
            raise ValidationError(_('No checklist template found for this certification type.'))

        # Clear existing items
        self.checklist_item_ids.unlink()

        # Create items from template
        for template_item in template.item_ids:
            self.env['property_fielder.inspection.checklist.item'].create({
                'inspection_id': self.id,
                'template_item_id': template_item.id,
                'sequence': template_item.sequence,
                'name': template_item.name,
                'category': template_item.category,
                'item_type': template_item.item_type,
                'is_mandatory': template_item.is_mandatory,
                'reading_unit': template_item.reading_unit,
                'reading_min': template_item.reading_min,
                'reading_max': template_item.reading_max,
                'help_text': template_item.help_text,
            })

        return True

    def action_schedule(self):
        """Schedule the inspection"""
        self.write({'state': 'scheduled'})

    def action_start(self):
        """Start the inspection"""
        self.write({'state': 'in_progress'})

    def action_complete(self):
        """Complete the inspection"""
        self.ensure_one()
        if not self.result:
            raise ValidationError(_('Please set the inspection result before completing!'))
        
        self.write({
            'state': 'completed',
            'completed_date': fields.Date.today()
        })
        
        # If passed, create certification
        if self.result == 'pass':
            self.action_generate_certificate()

    def action_fail(self):
        """Mark inspection as failed"""
        self.write({
            'state': 'failed',
            'result': 'fail',
            'completed_date': fields.Date.today()
        })

    def action_cancel(self):
        """Cancel the inspection"""
        self.write({'state': 'cancelled'})

    def action_sign_inspector(self):
        """Record inspector signature with timestamp."""
        self.ensure_one()
        if not self.inspector_signature:
            raise ValidationError(_('Please provide a signature before signing.'))
        self.write({
            'inspector_signature_date': fields.Datetime.now(),
            'inspector_signature_name': self.inspector_id.name if self.inspector_id else self.env.user.name,
        })
        return True

    def action_sign_witness(self):
        """Record witness signature with timestamp."""
        self.ensure_one()
        if not self.witness_signature:
            raise ValidationError(_('Please provide a witness signature before signing.'))
        if not self.witness_signature_name:
            raise ValidationError(_('Please enter the witness name.'))
        self.write({
            'witness_signature_date': fields.Datetime.now(),
            'is_witnessed': True,
        })
        return True

    def action_generate_certificate(self):
        """Generate a certification from this inspection"""
        self.ensure_one()
        
        if self.certification_id:
            raise ValidationError(_('Certificate already generated for this inspection!'))
        
        if self.result != 'pass':
            raise ValidationError(_('Can only generate certificate for passed inspections!'))
        
        # Create certification
        cert = self.env['property_fielder.property.certification'].create({
            'name': f'CERT-{self.name}',
            'property_id': self.property_id.id,
            'certification_type_id': self.certification_type_id.id,
            'issue_date': self.completed_date or fields.Date.today(),
            'expiry_date': (self.completed_date or fields.Date.today()) + 
                          timedelta(days=self.certification_type_id.validity_period),
            'inspector_id': self.inspector_id.partner_id.id if self.inspector_id else False,
            'inspection_id': self.id,
            'notes': self.findings,
        })
        
        self.certification_id = cert.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.property.certification',
            'res_id': cert.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_field_service_job(self):
        """Create a field service job for this inspection"""
        from datetime import datetime, timedelta

        self.ensure_one()

        if self.job_id:
            raise ValidationError(_('Field service job already created for this inspection!'))

        # Get property address fields
        prop = self.property_id

        # Calculate scheduled date and time windows
        scheduled_date = self.scheduled_date or fields.Date.today()
        # Default time window: 8am to 6pm on the scheduled date
        earliest_start = datetime.combine(scheduled_date, datetime.min.time().replace(hour=8))
        latest_end = datetime.combine(scheduled_date, datetime.min.time().replace(hour=18))

        # Get or create a default partner if property has none
        partner_id = prop.partner_id.id if prop.partner_id else self.env.ref('base.partner_admin').id

        # Create job with full address and all required fields
        job = self.env['property_fielder.job'].create({
            'name': f'Inspection: {self.certification_type_id.name} - {prop.name}',
            'partner_id': partner_id,
            'street': prop.street or prop.name,  # Use property name as fallback
            'street2': prop.street2,
            'city': prop.city or 'London',  # Default to London
            'state_id': False,  # UK doesn't typically use states
            'zip': prop.zip,
            'country_id': prop.country_id.id if prop.country_id else self.env.ref('base.uk').id,
            'latitude': prop.latitude or 51.5074,  # Default to London center
            'longitude': prop.longitude or -0.1278,
            'scheduled_date': scheduled_date,
            'earliest_start': earliest_start,
            'latest_end': latest_end,
            'duration_minutes': self.certification_type_id.default_duration_minutes or 60,
            'inspector_id': self.inspector_id.id if self.inspector_id else False,
            'notes': f'Property Inspection\nType: {self.certification_type_id.name}\nProperty: {prop.name}',
        })
        
        self.job_id = job.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.job',
            'res_id': job.id,
            'view_mode': 'form',
            'target': 'current',
        }


from datetime import timedelta

