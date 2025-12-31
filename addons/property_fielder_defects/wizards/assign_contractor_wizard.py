# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AssignContractorWizard(models.TransientModel):
    """Wizard to assign a contractor to a defect and send notification."""
    
    _name = 'property_fielder.assign.contractor.wizard'
    _description = 'Assign Contractor Wizard'
    
    defect_id = fields.Many2one(
        'property_fielder.defect',
        string='Defect',
        required=True,
        ondelete='cascade'
    )
    
    contractor_id = fields.Many2one(
        'res.partner',
        string='Contractor',
        domain=[('is_company', '=', True)],
        required=True
    )
    
    send_notification = fields.Boolean(
        string='Send Email Notification',
        default=True,
        help='Send email notification to the contractor about this assignment'
    )
    
    additional_notes = fields.Text(
        string='Additional Notes',
        help='Additional instructions for the contractor (included in email)'
    )
    
    # Display fields from defect
    property_name = fields.Char(
        related='defect_id.property_id.name',
        string='Property'
    )
    
    defect_description = fields.Text(
        related='defect_id.description',
        string='Defect Description'
    )
    
    severity = fields.Selection(
        related='defect_id.severity_sla',
        string='Severity'
    )
    
    deadline_date = fields.Date(
        related='defect_id.deadline_date',
        string='Deadline'
    )
    
    def action_assign(self):
        """Assign contractor and optionally send notification."""
        self.ensure_one()
        
        if not self.contractor_id:
            raise UserError(_('Please select a contractor.'))
        
        # Update defect with contractor
        self.defect_id.write({
            'assigned_contractor_id': self.contractor_id.id,
        })
        
        # Add notes as a message if provided
        if self.additional_notes:
            self.defect_id.message_post(
                body=_('Contractor Assignment Notes:\n%s') % self.additional_notes,
                message_type='comment'
            )
        
        # Note: notification is sent automatically via the write() override in defect.py
        # if send_notification was True, it will be handled there
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Contractor Assigned'),
                'message': _('Contractor %s has been assigned to defect %s') % (
                    self.contractor_id.name,
                    self.defect_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }

