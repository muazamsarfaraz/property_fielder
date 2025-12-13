# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class PropertyCertification(models.Model):
    _name = 'property_fielder.property.certification'
    _description = 'Property Certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date desc, issue_date desc'

    name = fields.Char(string='Certificate Number', required=True, tracking=True)
    
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
    
    # Dates
    issue_date = fields.Date(
        string='Issue Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    expiry_date = fields.Date(
        string='Expiry Date',
        required=True,
        tracking=True
    )
    
    next_inspection_date = fields.Date(
        string='Next Inspection Date',
        compute='_compute_next_inspection_date',
        store=True
    )
    
    days_until_expiry = fields.Integer(
        string='Days Until Expiry',
        compute='_compute_days_until_expiry',
        store=True
    )
    
    # Status
    status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', compute='_compute_status', store=True, tracking=True)
    
    # Inspector/Certifier
    inspector_id = fields.Many2one('res.partner', string='Inspector/Certifier', tracking=True)
    inspector_company = fields.Char(string='Inspector Company')
    inspector_license = fields.Char(string='Inspector License Number')
    
    # Certificate Details
    certificate_file = fields.Binary(string='Certificate File', attachment=True)
    certificate_filename = fields.Char(string='Certificate Filename')
    
    # Compliance
    is_compliant = fields.Boolean(
        string='Compliant',
        compute='_compute_is_compliant',
        store=True
    )
    
    compliance_notes = fields.Text(string='Compliance Notes')
    
    # Related Inspection
    inspection_id = fields.Many2one(
        'property_fielder.property.inspection',
        string='Related Inspection',
        ondelete='set null'
    )
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends('issue_date', 'certification_type_id.validity_period')
    def _compute_next_inspection_date(self):
        for cert in self:
            if cert.issue_date and cert.certification_type_id:
                cert.next_inspection_date = cert.issue_date + timedelta(
                    days=cert.certification_type_id.validity_period
                )
            else:
                cert.next_inspection_date = False

    @api.depends('expiry_date')
    def _compute_days_until_expiry(self):
        today = fields.Date.today()
        for cert in self:
            if cert.expiry_date:
                delta = cert.expiry_date - today
                cert.days_until_expiry = delta.days
            else:
                cert.days_until_expiry = 0

    @api.depends('expiry_date', 'certification_type_id.warning_period')
    def _compute_status(self):
        today = fields.Date.today()
        for cert in self:
            if not cert.expiry_date:
                cert.status = 'valid'
            elif cert.expiry_date < today:
                cert.status = 'expired'
            elif cert.certification_type_id and cert.expiry_date <= (
                today + timedelta(days=cert.certification_type_id.warning_period)
            ):
                cert.status = 'expiring_soon'
            else:
                cert.status = 'valid'

    @api.depends('status')
    def _compute_is_compliant(self):
        for cert in self:
            cert.is_compliant = cert.status in ['valid', 'expiring_soon']

    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for cert in self:
            if cert.issue_date and cert.expiry_date and cert.expiry_date <= cert.issue_date:
                raise ValidationError(_('Expiry date must be after issue date!'))

    @api.onchange('certification_type_id', 'issue_date')
    def _onchange_certification_type(self):
        if self.certification_type_id and self.issue_date:
            self.expiry_date = self.issue_date + timedelta(
                days=self.certification_type_id.validity_period
            )

    def action_renew(self):
        """Create a new certification based on this one"""
        self.ensure_one()
        new_cert = self.copy({
            'name': _('New'),
            'issue_date': fields.Date.today(),
            'expiry_date': fields.Date.today() + timedelta(
                days=self.certification_type_id.validity_period
            ),
            'certificate_file': False,
            'certificate_filename': False,
            'inspection_id': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.property.certification',
            'res_id': new_cert.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        self.write({'status': 'cancelled'})

