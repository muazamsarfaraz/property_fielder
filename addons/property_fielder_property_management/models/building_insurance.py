# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta


class BuildingInsurance(models.Model):
    _name = 'property_fielder.building.insurance'
    _description = 'Building Insurance Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date desc'

    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Policy Details
    policy_number = fields.Char(string='Policy Number', required=True, tracking=True)
    policy_type = fields.Selection([
        ('buildings', 'Buildings Only'),
        ('contents', 'Contents Only'),
        ('combined', 'Buildings & Contents'),
        ('landlord', 'Landlord Insurance'),
        ('block', 'Block Policy'),
        ('rent_guarantee', 'Rent Guarantee')
    ], string='Policy Type', required=True, default='landlord', tracking=True)
    
    # Provider
    insurer_id = fields.Many2one(
        'res.partner',
        string='Insurer',
        tracking=True
    )
    insurer_name = fields.Char(string='Insurer Name')
    broker_id = fields.Many2one(
        'res.partner',
        string='Broker',
        help='Insurance broker if applicable'
    )
    
    # Coverage Dates
    start_date = fields.Date(string='Policy Start', required=True, tracking=True)
    expiry_date = fields.Date(string='Policy Expiry', required=True, tracking=True)
    
    # Status
    status = fields.Selection([
        ('active', 'Active'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Renewal')
    ], string='Status', compute='_compute_status', store=True, tracking=True)
    
    days_until_expiry = fields.Integer(
        string='Days Until Expiry',
        compute='_compute_days_until_expiry',
        store=True
    )
    
    # Coverage Values
    buildings_sum = fields.Monetary(
        string='Buildings Sum Insured',
        currency_field='currency_id'
    )
    contents_sum = fields.Monetary(
        string='Contents Sum Insured',
        currency_field='currency_id'
    )
    liability_cover = fields.Monetary(
        string='Public Liability Cover',
        currency_field='currency_id'
    )
    rent_cover_months = fields.Integer(
        string='Rent Cover (Months)',
        help='Number of months rent covered for loss of rent'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Premium
    annual_premium = fields.Monetary(
        string='Annual Premium',
        currency_field='currency_id',
        tracking=True
    )
    payment_frequency = fields.Selection([
        ('annual', 'Annual'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ], string='Payment Frequency', default='annual')
    
    # Excess
    excess_amount = fields.Monetary(
        string='Excess',
        currency_field='currency_id'
    )
    subsidence_excess = fields.Monetary(
        string='Subsidence Excess',
        currency_field='currency_id'
    )
    
    # Special Conditions
    unoccupancy_clause = fields.Boolean(
        string='Unoccupancy Clause',
        help='Policy has restrictions if property left unoccupied'
    )
    unoccupancy_days = fields.Integer(
        string='Unoccupancy Limit (Days)',
        help='Maximum days property can be unoccupied'
    )
    
    # Documents
    policy_document = fields.Binary(string='Policy Document', attachment=True)
    policy_filename = fields.Char(string='Policy Filename')
    schedule_document = fields.Binary(string='Schedule', attachment=True)
    schedule_filename = fields.Char(string='Schedule Filename')
    
    notes = fields.Text(string='Notes')

    @api.depends('expiry_date')
    def _compute_days_until_expiry(self):
        today = fields.Date.today()
        for insurance in self:
            if insurance.expiry_date:
                delta = insurance.expiry_date - today
                insurance.days_until_expiry = delta.days
            else:
                insurance.days_until_expiry = 0

    @api.depends('expiry_date', 'start_date')
    def _compute_status(self):
        today = fields.Date.today()
        warning_days = 30
        for insurance in self:
            if not insurance.expiry_date:
                insurance.status = 'pending'
            elif insurance.expiry_date < today:
                insurance.status = 'expired'
            elif insurance.expiry_date <= (today + timedelta(days=warning_days)):
                insurance.status = 'expiring'
            elif insurance.start_date and insurance.start_date > today:
                insurance.status = 'pending'
            else:
                insurance.status = 'active'

