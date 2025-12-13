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
    
    photo_ids = fields.Many2many(
        'ir.attachment',
        string='Photos',
        help='Photos taken during inspection'
    )
    
    # Notes
    notes = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Inspection number must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('property_fielder.property.inspection') or _('New')
        return super(PropertyInspection, self).create(vals_list)

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

