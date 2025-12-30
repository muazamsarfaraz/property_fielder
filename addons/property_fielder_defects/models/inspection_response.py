# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InspectionResponse(models.Model):
    """Extend inspection response to link to defects."""
    
    _inherit = 'property_fielder.inspection.response'
    
    defect_id = fields.Many2one(
        'property_fielder.defect',
        string='Created Defect',
        ondelete='set null',
        help='Defect created from this response'
    )
    
    def action_create_defect(self):
        """Create defect from failed inspection response."""
        self.ensure_one()
        
        if not self.creates_defect:
            return False
        
        if self.defect_id:
            # Already has a defect
            return self.defect_id
        
        # Determine severity from template item
        severity_mapping = {
            'id': 'immediate',
            'ar': 'urgent',
            'ncs': 'advisory',
            'c1': 'immediate',
            'c2': 'urgent',
            'c3': 'advisory',
            'fi': 'advisory',
            'cat1': 'immediate',
            'cat2': 'standard',
        }
        
        item_severity = self.item_id.defect_severity or 'cat2'
        severity_sla = severity_mapping.get(item_severity, 'standard')
        
        # Find fault code if referenced
        fault_code = False
        if self.item_id.fault_code_reference:
            fault_code = self.env['property_fielder.fault.code'].search([
                ('code', '=', self.item_id.fault_code_reference)
            ], limit=1)
        
        # Create the defect
        defect = self.env['property_fielder.defect'].create({
            'property_id': self.inspection_id.property_id.id,
            'inspection_id': self.inspection_id.id,
            'response_id': self.id,
            'defect_type': 'regulatory_fault',
            'fault_code_id': fault_code.id if fault_code else False,
            'severity_sla': severity_sla,
            'description': f"{self.item_id.question}: {self.response_text or self.notes or 'Failed'}",
            'location': self.item_id.section_id.name if self.item_id.section_id else '',
        })
        
        self.defect_id = defect.id
        return defect
    
    def action_view_defect(self):
        """View the linked defect."""
        self.ensure_one()
        if not self.defect_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Defect'),
            'res_model': 'property_fielder.defect',
            'res_id': self.defect_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

