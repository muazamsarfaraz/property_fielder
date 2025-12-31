# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Owner Portal Access
    is_property_owner = fields.Boolean(
        string='Is Property Owner',
        help='Check if this contact is a property owner/landlord'
    )
    
    owner_portal_access = fields.Boolean(
        string='Portal Access',
        help='Grant access to the owner portal'
    )
    
    # Notification Preferences
    owner_notify_compliance = fields.Boolean(
        string='Compliance Notifications',
        default=True,
        help='Receive notifications about compliance status changes'
    )
    
    owner_notify_inspection = fields.Boolean(
        string='Inspection Notifications',
        default=True,
        help='Receive notifications about upcoming inspections'
    )
    
    owner_notify_certificate = fields.Boolean(
        string='Certificate Notifications',
        default=True,
        help='Receive notifications when certificates are uploaded'
    )
    
    # Computed fields for portal
    owned_property_ids = fields.One2many(
        'property_fielder.property',
        'partner_id',
        string='Owned Properties'
    )
    
    owned_property_count = fields.Integer(
        string='Property Count',
        compute='_compute_owned_property_count'
    )
    
    @api.depends('owned_property_ids')
    def _compute_owned_property_count(self):
        for partner in self:
            partner.owned_property_count = len(partner.owned_property_ids)
    
    def action_grant_portal_access(self):
        """Grant portal access to the owner"""
        self.ensure_one()
        self.write({
            'owner_portal_access': True,
        })
        # Also grant portal user group if not already
        portal_group = self.env.ref('base.group_portal')
        if self.user_ids:
            for user in self.user_ids:
                if portal_group not in user.groups_id:
                    user.groups_id = [(4, portal_group.id)]
        return True

