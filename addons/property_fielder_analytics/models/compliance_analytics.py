# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class ComplianceAnalytics(models.TransientModel):
    """Compliance trend analytics and reporting"""
    
    _name = 'property_fielder.compliance.analytics'
    _description = 'Compliance Analytics'
    
    # Filters
    date_from = fields.Date(
        string='From Date',
        default=lambda self: fields.Date.today() - timedelta(days=365)
    )
    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today
    )
    property_ids = fields.Many2many(
        'property_fielder.property',
        string='Properties',
        help='Leave empty for all properties'
    )
    certification_type_ids = fields.Many2many(
        'property_fielder.certification.type',
        string='Certification Types',
        help='Leave empty for all types'
    )
    
    # Summary Stats
    total_properties = fields.Integer(string='Total Properties', compute='_compute_stats')
    total_certifications = fields.Integer(string='Total Certifications', compute='_compute_stats')
    compliant_count = fields.Integer(string='Compliant', compute='_compute_stats')
    expiring_soon_count = fields.Integer(string='Expiring Soon (30 days)', compute='_compute_stats')
    expired_count = fields.Integer(string='Expired', compute='_compute_stats')
    compliance_rate = fields.Float(string='Compliance Rate (%)', compute='_compute_stats')
    
    # Trend data
    trend_line_ids = fields.One2many(
        'property_fielder.compliance.trend.line',
        'analytics_id',
        string='Monthly Trends'
    )
    
    # Category breakdown
    category_line_ids = fields.One2many(
        'property_fielder.compliance.category.line',
        'analytics_id',
        string='Category Breakdown'
    )
    
    @api.depends('property_ids', 'certification_type_ids')
    def _compute_stats(self):
        for record in self:
            # Get properties
            if record.property_ids:
                properties = record.property_ids
            else:
                properties = self.env['property_fielder.property'].search([])
            
            record.total_properties = len(properties)
            
            # Get certifications
            cert_domain = [('property_id', 'in', properties.ids)]
            if record.certification_type_ids:
                cert_domain.append(('certification_type_id', 'in', record.certification_type_ids.ids))
            
            certs = self.env['property_fielder.property.certification'].search(cert_domain)
            record.total_certifications = len(certs)
            
            today = fields.Date.today()
            soon = today + timedelta(days=30)
            
            record.compliant_count = len(certs.filtered(
                lambda c: c.status == 'valid' and (not c.expiry_date or c.expiry_date > soon)
            ))
            record.expiring_soon_count = len(certs.filtered(
                lambda c: c.expiry_date and today < c.expiry_date <= soon
            ))
            record.expired_count = len(certs.filtered(
                lambda c: c.expiry_date and c.expiry_date <= today
            ))
            
            if record.total_certifications:
                record.compliance_rate = round(
                    (record.compliant_count / record.total_certifications) * 100, 1
                )
            else:
                record.compliance_rate = 0.0
    
    def action_generate_trends(self):
        """Generate compliance trend analysis"""
        self.ensure_one()
        
        # Clear existing
        self.trend_line_ids.unlink()
        self.category_line_ids.unlink()
        
        # Get properties
        if self.property_ids:
            properties = self.property_ids
        else:
            properties = self.env['property_fielder.property'].search([])
        
        # Get certifications
        cert_domain = [('property_id', 'in', properties.ids)]
        if self.certification_type_ids:
            cert_domain.append(('certification_type_id', 'in', self.certification_type_ids.ids))
        
        certs = self.env['property_fielder.property.certification'].search(cert_domain)
        
        # Generate monthly trend
        trends = []
        current = self.date_from.replace(day=1)
        end = self.date_to
        
        while current <= end:
            month_end = (current.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            
            # Calculate compliance for this month
            valid_count = len(certs.filtered(
                lambda c: not c.expiry_date or c.expiry_date > current
            ))
            
            trends.append((0, 0, {
                'analytics_id': self.id,
                'month': current,
                'total_certs': len(certs),
                'valid_certs': valid_count,
                'compliance_rate': (valid_count / len(certs) * 100) if certs else 0,
            }))
            
            # Next month
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        self.trend_line_ids = trends
        
        # Generate category breakdown
        categories = defaultdict(lambda: {'total': 0, 'valid': 0, 'expired': 0})
        today = fields.Date.today()
        
        for cert in certs:
            cat = cert.certification_type_id.flage_category or 'other'
            categories[cat]['total'] += 1
            if cert.expiry_date and cert.expiry_date <= today:
                categories[cat]['expired'] += 1
            else:
                categories[cat]['valid'] += 1
        
        cat_lines = []
        for cat, data in categories.items():
            cat_lines.append((0, 0, {
                'analytics_id': self.id,
                'category': cat,
                'total_count': data['total'],
                'valid_count': data['valid'],
                'expired_count': data['expired'],
                'compliance_rate': (data['valid'] / data['total'] * 100) if data['total'] else 0,
            }))
        
        self.category_line_ids = cat_lines
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Analytics'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }


class ComplianceTrendLine(models.TransientModel):
    _name = 'property_fielder.compliance.trend.line'
    _description = 'Compliance Trend Line'
    
    analytics_id = fields.Many2one('property_fielder.compliance.analytics', ondelete='cascade')
    month = fields.Date(string='Month')
    total_certs = fields.Integer(string='Total Certificates')
    valid_certs = fields.Integer(string='Valid Certificates')
    compliance_rate = fields.Float(string='Compliance %')


class ComplianceCategoryLine(models.TransientModel):
    _name = 'property_fielder.compliance.category.line'
    _description = 'Compliance Category Line'
    
    analytics_id = fields.Many2one('property_fielder.compliance.analytics', ondelete='cascade')
    category = fields.Selection([
        ('fire', 'Fire Safety'),
        ('legionella', 'Legionella'),
        ('asbestos', 'Asbestos'),
        ('gas', 'Gas Safety'),
        ('electrical', 'Electrical'),
        ('epc', 'EPC'),
        ('other', 'Other'),
    ], string='Category')
    total_count = fields.Integer(string='Total')
    valid_count = fields.Integer(string='Valid')
    expired_count = fields.Integer(string='Expired')
    compliance_rate = fields.Float(string='Compliance %')

