# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError
import base64


class OwnerPortal(CustomerPortal):
    """Portal controller for property owners"""

    def _prepare_home_portal_values(self, counters):
        """Add property count to portal home"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'property_count' in counters:
            if partner.is_property_owner and partner.owner_portal_access:
                values['property_count'] = request.env['property_fielder.property'].search_count([
                    ('partner_id', '=', partner.id)
                ])
            else:
                values['property_count'] = 0
        
        return values

    def _check_owner_access(self):
        """Check if current user has owner portal access"""
        partner = request.env.user.partner_id
        if not partner.is_property_owner or not partner.owner_portal_access:
            raise AccessError(_("You don't have access to the owner portal."))
        return partner

    @http.route(['/my/properties', '/my/properties/page/<int:page>'], 
                type='http', auth='user', website=True)
    def portal_my_properties(self, page=1, sortby=None, **kw):
        """List owner's properties"""
        partner = self._check_owner_access()
        
        Property = request.env['property_fielder.property']
        domain = [('partner_id', '=', partner.id)]
        
        # Sorting options
        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name asc'},
            'compliance': {'label': _('Compliance'), 'order': 'compliance_status asc'},
            'city': {'label': _('City'), 'order': 'city asc'},
        }
        
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        
        # Count and pager
        property_count = Property.search_count(domain)
        pager = portal_pager(
            url='/my/properties',
            total=property_count,
            page=page,
            step=10,
        )
        
        # Get properties
        properties = Property.search(
            domain,
            order=order,
            limit=10,
            offset=pager['offset']
        )
        
        values = {
            'properties': properties,
            'page_name': 'properties',
            'pager': pager,
            'default_url': '/my/properties',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        }
        
        return request.render('property_fielder_owner_portal.portal_my_properties', values)

    @http.route('/my/properties/<int:property_id>', type='http', auth='user', website=True)
    def portal_property_detail(self, property_id, **kw):
        """Property detail view"""
        partner = self._check_owner_access()
        
        property_obj = request.env['property_fielder.property'].browse(property_id)
        
        # Check access
        if not property_obj.exists() or property_obj.partner_id.id != partner.id:
            raise AccessError(_("You don't have access to this property."))
        
        # Get certifications
        certifications = request.env['property_fielder.property.certification'].search([
            ('property_id', '=', property_id)
        ])
        
        # Get upcoming inspections
        inspections = request.env['property_fielder.property.inspection'].search([
            ('property_id', '=', property_id),
            ('state', 'in', ['draft', 'scheduled'])
        ], order='scheduled_date asc', limit=5)
        
        values = {
            'property': property_obj,
            'certifications': certifications,
            'inspections': inspections,
            'page_name': 'property_detail',
        }
        
        return request.render('property_fielder_owner_portal.portal_property_detail', values)

    @http.route('/my/properties/<int:property_id>/certificate/<int:cert_id>/download',
                type='http', auth='user', website=True)
    def download_certificate(self, property_id, cert_id, **kw):
        """Download a certificate PDF"""
        partner = self._check_owner_access()
        
        # Verify access
        property_obj = request.env['property_fielder.property'].browse(property_id)
        if not property_obj.exists() or property_obj.partner_id.id != partner.id:
            raise AccessError(_("You don't have access to this property."))
        
        cert = request.env['property_fielder.property.certification'].browse(cert_id)
        if not cert.exists() or cert.property_id.id != property_id:
            raise AccessError(_("Certificate not found."))
        
        if not cert.certificate_file:
            return request.redirect('/my/properties/%s' % property_id)
        
        # Return file download
        return request.make_response(
            base64.b64decode(cert.certificate_file),
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{cert.name}.pdf"'),
            ]
        )

    @http.route(['/my/inspections', '/my/inspections/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_inspections(self, page=1, **kw):
        """List all upcoming inspections for owner's properties"""
        partner = self._check_owner_access()

        Inspection = request.env['property_fielder.property.inspection']
        domain = [
            ('property_id.partner_id', '=', partner.id),
            ('state', 'in', ['draft', 'scheduled'])
        ]

        # Count and pager
        inspection_count = Inspection.search_count(domain)
        pager = portal_pager(
            url='/my/inspections',
            total=inspection_count,
            page=page,
            step=10,
        )

        # Get inspections
        inspections = Inspection.search(
            domain,
            order='scheduled_date asc',
            limit=10,
            offset=pager['offset']
        )

        values = {
            'inspections': inspections,
            'page_name': 'inspections',
            'pager': pager,
            'default_url': '/my/inspections',
        }

        return request.render('property_fielder_owner_portal.portal_my_inspections', values)

    @http.route('/my/inspections/<int:inspection_id>/reschedule',
                type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_reschedule_inspection(self, inspection_id, **kw):
        """Request reschedule for an inspection"""
        partner = self._check_owner_access()

        inspection = request.env['property_fielder.property.inspection'].browse(inspection_id)

        # Check access
        if not inspection.exists() or inspection.property_id.partner_id.id != partner.id:
            raise AccessError(_("You don't have access to this inspection."))

        if request.httprequest.method == 'POST':
            # Process reschedule request
            preferred_date = kw.get('preferred_date')
            preferred_time = kw.get('preferred_time', 'morning')
            reason = kw.get('reason', '')

            # Create reschedule request note
            message = _(
                "Owner Reschedule Request:\n"
                "Preferred Date: %s\n"
                "Preferred Time: %s\n"
                "Reason: %s"
            ) % (preferred_date, preferred_time, reason)

            inspection.message_post(body=message, message_type='comment')

            # If linked to a job, mark for reoptimization
            if inspection.job_id:
                inspection.job_id.write({
                    'confirmation_state': 'reschedule_requested',
                    'proposed_reschedule_date': preferred_date,
                })
                if inspection.job_id.route_id:
                    inspection.job_id.route_id.write({
                        'needs_reoptimization': True,
                        'reoptimization_reason': _('Owner requested reschedule'),
                    })

            return request.redirect('/my/inspections?reschedule_requested=1')

        values = {
            'inspection': inspection,
            'page_name': 'reschedule',
        }

        return request.render('property_fielder_owner_portal.portal_reschedule_form', values)

