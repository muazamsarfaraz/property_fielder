# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta


class EWS1Assessment(models.Model):
    """EWS1 External Wall System Assessment.
    
    Required for high-rise residential buildings following Grenfell.
    The EWS1 form assesses external wall fire risk and is often
    required for mortgage lending and valuations.
    """
    _name = 'property_fielder.ews1.assessment'
    _description = 'EWS1 External Wall Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assessment_date desc'

    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property/Block',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Assessment Details
    ews1_number = fields.Char(string='EWS1 Form Number', tracking=True)
    assessment_date = fields.Date(string='Assessment Date', required=True, tracking=True)
    
    assessor_id = fields.Many2one(
        'res.partner',
        string='Fire Safety Engineer',
        tracking=True
    )
    assessor_company = fields.Char(string='Assessor Company')
    assessor_registration = fields.Char(
        string='Registration Number',
        help='RICS/IFE/RIBA registration number'
    )
    
    # EWS1 Rating (A1 is best, B2 is worst)
    rating = fields.Selection([
        ('a1', 'A1 - No combustible materials'),
        ('a2', 'A2 - Combustible but fire risk low'),
        ('a3', 'A3 - Combustible, remediation needed'),
        ('b1', 'B1 - ACM/MCM cladding, risk addressed'),
        ('b2', 'B2 - ACM/MCM cladding, remediation needed'),
        ('fail', 'Fail/Not Assessed')
    ], string='EWS1 Rating', required=True, tracking=True)
    
    # Status
    status = fields.Selection([
        ('valid', 'Valid'),
        ('pending_works', 'Pending Remediation'),
        ('works_complete', 'Works Complete'),
        ('expired', 'Expired/Needs Reassessment'),
        ('not_required', 'Not Required')
    ], string='Status', compute='_compute_status', store=True, tracking=True)
    
    # Building Details Assessed
    building_height_m = fields.Float(string='Building Height (m)')
    number_of_storeys = fields.Integer(string='Number of Storeys')
    cladding_type = fields.Selection([
        ('acm', 'ACM (Aluminium Composite Material)'),
        ('hpl', 'HPL (High Pressure Laminate)'),
        ('render', 'External Render'),
        ('brick', 'Brick/Stone'),
        ('timber', 'Timber'),
        ('glass', 'Glass Curtain Wall'),
        ('mixed', 'Mixed Types'),
        ('none', 'No Cladding')
    ], string='Cladding Type')
    
    # Remediation
    remediation_required = fields.Boolean(string='Remediation Required', tracking=True)
    remediation_cost = fields.Monetary(
        string='Estimated Remediation Cost',
        currency_field='currency_id'
    )
    remediation_start_date = fields.Date(string='Remediation Start')
    remediation_completion_date = fields.Date(string='Remediation Completed')
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Funding
    funding_source = fields.Selection([
        ('building_safety_fund', 'Building Safety Fund'),
        ('freeholder', 'Freeholder'),
        ('leaseholders', 'Leaseholders'),
        ('developer', 'Original Developer'),
        ('mixed', 'Mixed Sources'),
        ('tbc', 'To Be Confirmed')
    ], string='Funding Source')
    
    # Documents
    ews1_form = fields.Binary(string='EWS1 Form', attachment=True)
    ews1_form_filename = fields.Char(string='EWS1 Filename')
    fire_risk_assessment = fields.Binary(string='Fire Risk Assessment', attachment=True)
    fra_filename = fields.Char(string='FRA Filename')
    
    # Validity
    valid_until = fields.Date(
        string='Valid Until',
        help='EWS1 forms are typically valid for 5 years'
    )
    
    notes = fields.Text(string='Notes')

    @api.depends('rating', 'remediation_required', 'remediation_completion_date', 'valid_until')
    def _compute_status(self):
        today = fields.Date.today()
        for ews in self:
            if ews.rating in ('a1', 'a2', 'b1'):
                if ews.valid_until and ews.valid_until < today:
                    ews.status = 'expired'
                else:
                    ews.status = 'valid'
            elif ews.rating in ('a3', 'b2', 'fail'):
                if ews.remediation_completion_date:
                    ews.status = 'works_complete'
                elif ews.remediation_required:
                    ews.status = 'pending_works'
                else:
                    ews.status = 'pending_works'
            else:
                ews.status = 'not_required'

    @api.onchange('assessment_date')
    def _onchange_assessment_date(self):
        """Auto-set valid_until to 5 years from assessment"""
        if self.assessment_date:
            self.valid_until = self.assessment_date + timedelta(days=365*5)

