# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class EmailReportWizard(models.TransientModel):
    """Wizard to email reports to recipients"""
    
    _name = 'property_fielder.email.report.wizard'
    _description = 'Email Report Wizard'
    
    # Report Selection
    report_type = fields.Selection([
        ('certificate', 'Certificate'),
        ('inspection', 'Inspection Report'),
        ('compliance', 'Property Compliance Summary'),
        ('portfolio', 'Portfolio Report'),
        ('hhsrs', 'HHSRS Assessment'),
        ('dhs', 'DHS Assessment'),
    ], string='Report Type', required=True, default='certificate')
    
    # Record selection (varies by report type)
    certification_id = fields.Many2one(
        'property_fielder.property.certification',
        string='Certificate'
    )
    inspection_id = fields.Many2one(
        'property_fielder.property.inspection',
        string='Inspection'
    )
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property'
    )
    hhsrs_assessment_id = fields.Many2one(
        'property_fielder.hhsrs.assessment',
        string='HHSRS Assessment'
    )
    dhs_assessment_id = fields.Many2one(
        'property_fielder.dhs.assessment',
        string='DHS Assessment'
    )
    
    # Recipients
    recipient_ids = fields.Many2many(
        'res.partner',
        string='Recipients',
        help='Select recipients to send the report to'
    )
    additional_emails = fields.Char(
        string='Additional Email Addresses',
        help='Comma-separated list of email addresses'
    )
    
    # Email Content
    email_subject = fields.Char(
        string='Subject',
        compute='_compute_email_defaults',
        store=True,
        readonly=False
    )
    email_body = fields.Html(
        string='Message',
        compute='_compute_email_defaults',
        store=True,
        readonly=False
    )
    
    # Options
    send_copy_to_self = fields.Boolean(
        string='Send Copy to Myself',
        default=True
    )
    include_related_docs = fields.Boolean(
        string='Include Related Documents',
        help='Attach related documents (e.g., photos, supporting files)'
    )
    
    @api.depends('report_type', 'certification_id', 'inspection_id', 'property_id')
    def _compute_email_defaults(self):
        for wizard in self:
            # Set default subject based on report type
            if wizard.report_type == 'certificate' and wizard.certification_id:
                cert = wizard.certification_id
                wizard.email_subject = f"Certificate: {cert.certification_type_id.name} - {cert.property_id.name}"
                wizard.email_body = f"""
<p>Dear recipient,</p>
<p>Please find attached the <strong>{cert.certification_type_id.name}</strong> certificate for the property at:</p>
<p><strong>{cert.property_id.name}</strong><br/>
{cert.property_id.street or ''}, {cert.property_id.city or ''} {cert.property_id.zip or ''}</p>
<p>Certificate valid until: <strong>{cert.expiry_date or 'N/A'}</strong></p>
<p>Best regards,<br/>Property Fielder</p>
"""
            elif wizard.report_type == 'inspection' and wizard.inspection_id:
                insp = wizard.inspection_id
                wizard.email_subject = f"Inspection Report: {insp.name}"
                wizard.email_body = f"""
<p>Dear recipient,</p>
<p>Please find attached the inspection report for:</p>
<p><strong>{insp.property_id.name}</strong><br/>
{insp.certification_type_id.name}</p>
<p>Inspection Date: <strong>{insp.scheduled_date or 'Not scheduled'}</strong></p>
<p>Best regards,<br/>Property Fielder</p>
"""
            elif wizard.report_type == 'compliance' and wizard.property_id:
                prop = wizard.property_id
                wizard.email_subject = f"Compliance Summary: {prop.name}"
                wizard.email_body = f"""
<p>Dear recipient,</p>
<p>Please find attached the compliance summary for:</p>
<p><strong>{prop.name}</strong><br/>
{prop.street or ''}, {prop.city or ''}</p>
<p>Best regards,<br/>Property Fielder</p>
"""
            else:
                wizard.email_subject = f"Property Fielder Report"
                wizard.email_body = """
<p>Dear recipient,</p>
<p>Please find the requested report attached.</p>
<p>Best regards,<br/>Property Fielder</p>
"""
    
    def action_send_report(self):
        """Generate and send the report via email"""
        self.ensure_one()
        
        # Validate recipients
        emails = self._get_recipient_emails()
        if not emails:
            raise UserError(_('Please select at least one recipient or enter email addresses.'))
        
        # Generate PDF report
        pdf_content, filename = self._generate_report_pdf()
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
        })
        
        attachment_ids = [attachment.id]
        
        # Include related documents if requested
        if self.include_related_docs:
            attachment_ids.extend(self._get_related_attachments())
        
        # Send email
        emails_sent = 0
        for email in emails:
            mail_values = {
                'subject': self.email_subject,
                'email_to': email,
                'body_html': self.email_body,
                'attachment_ids': [(6, 0, attachment_ids)],
                'auto_delete': True,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
            emails_sent += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Report Sent'),
                'message': _('Report sent to %d recipient(s).') % emails_sent,
                'type': 'success',
                'sticky': False,
            }
        }

    def _get_recipient_emails(self):
        """Get all recipient email addresses"""
        emails = []

        # From selected partners
        for partner in self.recipient_ids:
            if partner.email:
                emails.append(partner.email)

        # From additional emails field
        if self.additional_emails:
            for email in self.additional_emails.split(','):
                email = email.strip()
                if email and '@' in email:
                    emails.append(email)

        # Send copy to self
        if self.send_copy_to_self and self.env.user.email:
            emails.append(self.env.user.email)

        return list(set(emails))  # Remove duplicates

    def _generate_report_pdf(self):
        """Generate the PDF report based on type"""
        report_ref = None
        record = None
        filename = 'report.pdf'

        if self.report_type == 'certificate' and self.certification_id:
            report_ref = 'property_fielder_property_management.action_report_certificate'
            record = self.certification_id
            filename = f"Certificate_{record.certification_type_id.name}_{record.property_id.name}.pdf"

        elif self.report_type == 'inspection' and self.inspection_id:
            report_ref = 'property_fielder_property_management.action_report_inspection'
            record = self.inspection_id
            filename = f"Inspection_{record.name}.pdf"

        elif self.report_type == 'compliance' and self.property_id:
            report_ref = 'property_fielder_property_management.action_report_property_compliance'
            record = self.property_id
            filename = f"Compliance_{record.name}.pdf"

        elif self.report_type == 'portfolio':
            report_ref = 'property_fielder_property_management.action_report_portfolio_compliance'
            record = self.env['property_fielder.property'].search([])
            filename = f"Portfolio_Report_{fields.Date.today()}.pdf"

        elif self.report_type == 'hhsrs' and self.hhsrs_assessment_id:
            report_ref = 'property_fielder_hhsrs.action_report_hhsrs_assessment'
            record = self.hhsrs_assessment_id
            filename = f"HHSRS_{record.name}.pdf"

        elif self.report_type == 'dhs' and self.dhs_assessment_id:
            report_ref = 'property_fielder_hhsrs.action_report_dhs_assessment'
            record = self.dhs_assessment_id
            filename = f"DHS_{record.name}.pdf"

        if not report_ref or not record:
            raise UserError(_('Please select a record to generate the report.'))

        # Generate PDF
        report = self.env.ref(report_ref, raise_if_not_found=False)
        if not report:
            raise UserError(_('Report template not found: %s') % report_ref)

        pdf_content, _ = report._render_qweb_pdf(record.ids)

        # Clean filename
        filename = filename.replace(' ', '_').replace('/', '-')

        return pdf_content, filename

    def _get_related_attachments(self):
        """Get related document attachment IDs"""
        attachment_ids = []

        if self.report_type == 'certificate' and self.certification_id:
            # Get certificate attachment if exists
            if self.certification_id.attachment_id:
                attachment_ids.append(self.certification_id.attachment_id.id)

        elif self.report_type == 'inspection' and self.inspection_id:
            # Get inspection photos
            for photo in self.inspection_id.photo_ids:
                if photo.image:
                    att = self.env['ir.attachment'].create({
                        'name': f"Photo_{photo.id}.jpg",
                        'type': 'binary',
                        'datas': photo.image,
                        'mimetype': 'image/jpeg',
                    })
                    attachment_ids.append(att.id)

        return attachment_ids

