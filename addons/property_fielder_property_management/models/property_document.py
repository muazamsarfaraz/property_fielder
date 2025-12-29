# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PropertyDocument(models.Model):
    _name = 'property_fielder.property.document'
    _description = 'Property Document'
    _order = 'category, name'
    _inherit = ['mail.thread']

    name = fields.Char(string='Document Name', required=True)
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade'
    )
    
    category = fields.Selection([
        ('lease', 'Lease/Tenancy Agreement'),
        ('insurance', 'Insurance'),
        ('certificate', 'Certificates'),
        ('plan', 'Floor Plans/Drawings'),
        ('inventory', 'Inventory'),
        ('correspondence', 'Correspondence'),
        ('other', 'Other')
    ], string='Category', required=True, default='other')
    
    # Document file using ir.attachment pattern
    document_file = fields.Binary(
        string='Document',
        attachment=True,
        required=True
    )
    document_filename = fields.Char(string='Filename')
    
    # Metadata
    description = fields.Text(string='Description')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    
    # Status
    is_active = fields.Boolean(string='Active', default=True)
    is_expired = fields.Boolean(
        string='Expired',
        compute='_compute_is_expired',
        store=True
    )
    
    # Tracking
    uploaded_by = fields.Many2one(
        'res.users',
        string='Uploaded By',
        default=lambda self: self.env.user,
        readonly=True
    )
    upload_date = fields.Datetime(
        string='Upload Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for doc in self:
            if doc.expiry_date:
                doc.is_expired = doc.expiry_date < today
            else:
                doc.is_expired = False
    
    def name_get(self):
        result = []
        for doc in self:
            category_label = dict(self._fields['category'].selection).get(doc.category, '')
            name = f"[{category_label}] {doc.name}"
            result.append((doc.id, name))
        return result

