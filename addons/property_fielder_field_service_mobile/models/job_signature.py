# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobSignature(models.Model):
    """Customer signatures for job completion"""
    
    _name = 'property_fielder.job.signature'
    _description = 'Job Signature'
    _order = 'signed_time desc'
    
    # Job Reference
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        required=True,
        ondelete='cascade',
        help='Job this signature belongs to'
    )
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        help='Inspector who collected the signature'
    )
    
    # Signature Details
    signature = fields.Binary(
        string='Signature',
        required=True,
        attachment=True,
        help='Customer signature image'
    )
    
    signer_name = fields.Char(
        string='Signer Name',
        required=True,
        help='Name of person who signed'
    )
    
    signer_title = fields.Char(
        string='Signer Title',
        help='Title/role of signer (e.g., Homeowner, Property Manager)'
    )
    
    signer_email = fields.Char(
        string='Signer Email',
        help='Email address of signer'
    )
    
    signer_phone = fields.Char(
        string='Signer Phone',
        help='Phone number of signer'
    )
    
    # Timestamp
    signed_time = fields.Datetime(
        string='Signed Time',
        required=True,
        default=fields.Datetime.now,
        help='When signature was captured'
    )
    
    # Location
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS latitude where signature was captured'
    )
    
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS longitude where signature was captured'
    )
    
    # Type
    signature_type = fields.Selection([
        ('completion', 'Job Completion'),
        ('approval', 'Work Approval'),
        ('receipt', 'Receipt Acknowledgment'),
        ('other', 'Other')
    ], string='Signature Type', default='completion', required=True)
    
    # Notes
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the signature'
    )
    
    # Agreement Text
    agreement_text = fields.Text(
        string='Agreement Text',
        help='Text that signer agreed to'
    )
    
    # Device Info
    device_info = fields.Char(
        string='Device Info',
        help='Device information'
    )
    
    # IP Address
    ip_address = fields.Char(
        string='IP Address',
        help='IP address of device'
    )
    
    def action_send_copy(self):
        """Send copy of signature to signer email"""
        self.ensure_one()
        
        if not self.signer_email:
            raise ValidationError(_('No email address provided!'))
        
        # TODO: Implement email sending
        # template = self.env.ref('property_fielder_field_service_mobile.signature_email_template')
        # template.send_mail(self.id, force_send=True)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Signature copy sent to %s') % self.signer_email,
                'type': 'success',
            }
        }

