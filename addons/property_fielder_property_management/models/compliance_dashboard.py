# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta


class ComplianceDashboard(models.TransientModel):
    """Transient model for compliance dashboard statistics."""
    _name = 'property_fielder.compliance.dashboard'
    _description = 'Compliance Dashboard'

    # Summary Statistics
    total_properties = fields.Integer(string='Total Properties', compute='_compute_stats')
    compliant_count = fields.Integer(string='Compliant', compute='_compute_stats')
    expiring_30_count = fields.Integer(string='Expiring in 30 Days', compute='_compute_stats')
    expiring_60_count = fields.Integer(string='Expiring in 60 Days', compute='_compute_stats')
    expiring_90_count = fields.Integer(string='Expiring in 90 Days', compute='_compute_stats')
    expired_count = fields.Integer(string='Expired', compute='_compute_stats')
    non_compliant_count = fields.Integer(string='Non-Compliant', compute='_compute_stats')
    
    # Percentages
    compliance_percentage = fields.Float(string='Compliance %', compute='_compute_stats')
    
    # FLAGE+ Breakdown
    fire_compliant = fields.Integer(string='Fire Safety Compliant', compute='_compute_flage_stats')
    fire_issues = fields.Integer(string='Fire Safety Issues', compute='_compute_flage_stats')
    legionella_compliant = fields.Integer(string='Legionella Compliant', compute='_compute_flage_stats')
    legionella_issues = fields.Integer(string='Legionella Issues', compute='_compute_flage_stats')
    asbestos_compliant = fields.Integer(string='Asbestos Compliant', compute='_compute_flage_stats')
    asbestos_issues = fields.Integer(string='Asbestos Issues', compute='_compute_flage_stats')
    gas_compliant = fields.Integer(string='Gas Safety Compliant', compute='_compute_flage_stats')
    gas_issues = fields.Integer(string='Gas Safety Issues', compute='_compute_flage_stats')
    electrical_compliant = fields.Integer(string='Electrical Compliant', compute='_compute_flage_stats')
    electrical_issues = fields.Integer(string='Electrical Issues', compute='_compute_flage_stats')
    epc_compliant = fields.Integer(string='EPC Compliant', compute='_compute_flage_stats')
    epc_issues = fields.Integer(string='EPC Issues', compute='_compute_flage_stats')
    
    # Inspection Stats
    pending_inspections = fields.Integer(string='Pending Inspections', compute='_compute_inspection_stats')
    overdue_inspections = fields.Integer(string='Overdue Inspections', compute='_compute_inspection_stats')
    inspections_this_month = fields.Integer(string='Inspections This Month', compute='_compute_inspection_stats')
    
    @api.depends_context('uid')
    def _compute_stats(self):
        Property = self.env['property_fielder.property']
        Certification = self.env['property_fielder.property.certification']
        today = fields.Date.today()
        
        for rec in self:
            properties = Property.search([])
            rec.total_properties = len(properties)
            
            rec.compliant_count = Property.search_count([('compliance_status', '=', 'compliant')])
            rec.expired_count = Property.search_count([('compliance_status', '=', 'expired')])
            rec.non_compliant_count = Property.search_count([('compliance_status', '=', 'non_compliant')])
            
            # Expiring certifications
            rec.expiring_30_count = Certification.search_count([
                ('status', '=', 'expiring_soon'),
                ('expiry_date', '<=', today + timedelta(days=30)),
                ('expiry_date', '>', today)
            ])
            rec.expiring_60_count = Certification.search_count([
                ('expiry_date', '<=', today + timedelta(days=60)),
                ('expiry_date', '>', today + timedelta(days=30))
            ])
            rec.expiring_90_count = Certification.search_count([
                ('expiry_date', '<=', today + timedelta(days=90)),
                ('expiry_date', '>', today + timedelta(days=60))
            ])
            
            # Compliance percentage
            if rec.total_properties > 0:
                rec.compliance_percentage = (rec.compliant_count / rec.total_properties) * 100
            else:
                rec.compliance_percentage = 0

    @api.depends_context('uid')
    def _compute_flage_stats(self):
        Property = self.env['property_fielder.property']
        
        for rec in self:
            rec.fire_compliant = Property.search_count([('flage_fire_status', '=', 'valid')])
            rec.fire_issues = Property.search_count([('flage_fire_status', 'in', ['expired', 'missing'])])
            
            rec.legionella_compliant = Property.search_count([('flage_legionella_status', '=', 'valid')])
            rec.legionella_issues = Property.search_count([('flage_legionella_status', 'in', ['expired', 'missing'])])
            
            rec.asbestos_compliant = Property.search_count([('flage_asbestos_status', '=', 'valid')])
            rec.asbestos_issues = Property.search_count([('flage_asbestos_status', 'in', ['expired', 'missing'])])
            
            rec.gas_compliant = Property.search_count([('flage_gas_status', '=', 'valid')])
            rec.gas_issues = Property.search_count([('flage_gas_status', 'in', ['expired', 'missing'])])
            
            rec.electrical_compliant = Property.search_count([('flage_electrical_status', '=', 'valid')])
            rec.electrical_issues = Property.search_count([('flage_electrical_status', 'in', ['expired', 'missing'])])
            
            rec.epc_compliant = Property.search_count([('flage_epc_status', '=', 'valid')])
            rec.epc_issues = Property.search_count([('flage_epc_status', 'in', ['expired', 'missing'])])

    @api.depends_context('uid')
    def _compute_inspection_stats(self):
        Inspection = self.env['property_fielder.property.inspection']
        today = fields.Date.today()
        first_of_month = today.replace(day=1)
        
        for rec in self:
            rec.pending_inspections = Inspection.search_count([
                ('state', 'in', ['draft', 'scheduled']),
                ('scheduled_date', '>=', today)
            ])
            rec.overdue_inspections = Inspection.search_count([
                ('state', 'in', ['draft', 'scheduled']),
                ('scheduled_date', '<', today)
            ])
            rec.inspections_this_month = Inspection.search_count([
                ('state', '=', 'completed'),
                ('completed_date', '>=', first_of_month)
            ])

    def action_view_compliant(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliant Properties'),
            'res_model': 'property_fielder.property',
            'view_mode': 'kanban,list,form',
            'domain': [('compliance_status', '=', 'compliant')],
        }

    def action_view_expired(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expired Certifications'),
            'res_model': 'property_fielder.property',
            'view_mode': 'kanban,list,form',
            'domain': [('compliance_status', '=', 'expired')],
        }

    def action_view_expiring(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expiring Soon'),
            'res_model': 'property_fielder.property.certification',
            'view_mode': 'list,form',
            'domain': [('status', '=', 'expiring_soon')],
        }

    def action_view_overdue_inspections(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Overdue Inspections'),
            'res_model': 'property_fielder.property.inspection',
            'view_mode': 'list,form',
            'domain': [('state', 'in', ['draft', 'scheduled']), ('scheduled_date', '<', fields.Date.today())],
        }

    def action_view_status_chart(self):
        """View certification status pie chart."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certification Status'),
            'res_model': 'property_fielder.property.certification',
            'view_mode': 'graph,list,form',
            'context': {'graph_mode': 'pie'},
        }

    def action_view_flage_chart(self):
        """View FLAGE+ category pie chart."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('By FLAGE+ Category'),
            'res_model': 'property_fielder.property.certification',
            'view_mode': 'graph,list,form',
            'context': {'graph_groupbys': ['flage_category']},
        }

    def action_view_expiry_chart(self):
        """View expiry timeline chart."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expiry Timeline'),
            'res_model': 'property_fielder.property.certification',
            'view_mode': 'graph,list,form',
            'context': {'graph_mode': 'bar', 'graph_groupbys': ['expiry_date:month']},
        }

    def action_view_pivot_analysis(self):
        """View pivot analysis."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certification Analysis'),
            'res_model': 'property_fielder.property.certification',
            'view_mode': 'pivot,graph,list,form',
        }

    def action_schedule_overdue_inspections(self):
        """Open wizard to schedule all overdue inspections."""
        # Get overdue inspections
        Inspection = self.env['property_fielder.property.inspection']
        overdue = Inspection.search([
            ('state', 'in', ['draft', 'scheduled']),
            ('scheduled_date', '<', fields.Date.today())
        ])
        if not overdue:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Overdue Inspections'),
                    'message': _('All inspections are up to date!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Overdue Inspections'),
            'res_model': 'property_fielder.property.inspection',
            'view_mode': 'list,form',
            'domain': [('id', 'in', overdue.ids)],
            'context': {'create': False},
        }

    def action_generate_portfolio_report(self):
        """Generate portfolio compliance report."""
        return self.env.ref(
            'property_fielder_property_management.action_report_portfolio_compliance'
        ).report_action(self.env['property_fielder.property'].search([]))

    def action_send_expiry_reminders(self):
        """Send reminder notifications for expiring certifications."""
        Certification = self.env['property_fielder.property.certification']
        today = fields.Date.today()
        expiring = Certification.search([
            ('status', '=', 'expiring_soon'),
            ('expiry_date', '<=', today + timedelta(days=30))
        ])
        count = 0
        for cert in expiring:
            # Post reminder on certification chatter
            cert.message_post(
                body=_('Reminder: This certification expires on %s. Please schedule renewal.') % cert.expiry_date,
                subject=_('Certification Expiry Reminder'),
                message_type='notification',
            )
            count += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reminders Sent'),
                'message': _('%d expiry reminder(s) posted to certifications.') % count,
                'type': 'success',
                'sticky': False,
            }
        }

