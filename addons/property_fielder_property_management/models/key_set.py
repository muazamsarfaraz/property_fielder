# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KeySet(models.Model):
    _name = 'property_fielder.key.set'
    _description = 'Property Key Set'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'property_id, name'

    name = fields.Char(
        string='Key Set Name',
        required=True,
        help='e.g., "Main Set", "Spare Set", "Agent Copy"'
    )
    
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Key Details
    key_type = fields.Selection([
        ('full_set', 'Full Set (All Keys)'),
        ('front_door', 'Front Door Only'),
        ('communal', 'Communal/Building Keys'),
        ('garage', 'Garage/Parking'),
        ('mailbox', 'Mailbox'),
        ('other', 'Other')
    ], string='Key Type', default='full_set', required=True)
    
    key_count = fields.Integer(
        string='Number of Keys',
        default=1,
        help='How many physical keys in this set'
    )
    
    fob_count = fields.Integer(
        string='Number of Fobs',
        default=0,
        help='Electronic fobs/cards in this set'
    )
    
    # Current Holder
    holder_id = fields.Many2one(
        'res.partner',
        string='Current Holder',
        tracking=True,
        help='Person or company currently holding these keys'
    )
    holder_type = fields.Selection([
        ('owner', 'Owner/Landlord'),
        ('tenant', 'Tenant'),
        ('agent', 'Managing Agent'),
        ('contractor', 'Contractor'),
        ('keysafe', 'Key Safe'),
        ('office', 'Office/On-site')
    ], string='Holder Type')
    
    # Location
    storage_location = fields.Char(
        string='Storage Location',
        help='Where keys are stored (if keysafe or office)'
    )
    keysafe_code = fields.Char(
        string='Key Safe Code',
        groups='property_fielder_property_management.group_property_manager'
    )
    
    # Status
    state = fields.Selection([
        ('available', 'Available'),
        ('checked_out', 'Checked Out'),
        ('lost', 'Lost'),
        ('returned', 'Returned'),
        ('destroyed', 'Destroyed')
    ], string='Status', default='available', tracking=True)
    
    # Tracking
    checkout_date = fields.Datetime(
        string='Last Checkout',
        tracking=True
    )
    expected_return_date = fields.Date(
        string='Expected Return'
    )
    return_date = fields.Datetime(
        string='Returned On'
    )
    
    # Audit Trail via History
    history_ids = fields.One2many(
        'property_fielder.key.history',
        'key_set_id',
        string='Key History'
    )
    
    notes = fields.Text(string='Notes')
    
    def action_checkout(self):
        """Check out keys to a holder"""
        self.ensure_one()
        return {
            'name': _('Check Out Keys'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.key.checkout.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_key_set_id': self.id},
        }
    
    def action_return(self):
        """Return keys"""
        self.ensure_one()
        self._create_history('return')
        self.write({
            'state': 'available',
            'return_date': fields.Datetime.now(),
            'holder_id': False,
            'holder_type': False,
        })
    
    def action_report_lost(self):
        """Report keys as lost"""
        self.ensure_one()
        self._create_history('lost')
        self.write({'state': 'lost'})
    
    def _create_history(self, action_type):
        """Create a history record for key actions"""
        self.env['property_fielder.key.history'].create({
            'key_set_id': self.id,
            'action_type': action_type,
            'holder_id': self.holder_id.id if self.holder_id else False,
            'performed_by_id': self.env.user.partner_id.id,
        })

