# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BulkUploadCertificatesWizard(models.TransientModel):
    """Wizard for bulk uploading certificates from CSV/Excel.
    
    Expected CSV format:
    property_ref, certification_type_code, certificate_number, issue_date, expiry_date, issuer, notes
    """
    _name = 'property_fielder.bulk.upload.certificates.wizard'
    _description = 'Bulk Upload Certificates Wizard'

    file = fields.Binary(
        string='CSV File',
        required=True,
        help='Upload a CSV file with certificate data'
    )
    filename = fields.Char(string='Filename')

    # Options
    update_existing = fields.Boolean(
        string='Update Existing Certificates',
        default=False,
        help='If checked, existing certificates will be updated. Otherwise, duplicates are skipped.'
    )
    skip_errors = fields.Boolean(
        string='Skip Rows with Errors',
        default=True,
        help='Continue processing even if some rows have errors'
    )

    # Results
    preview_lines = fields.Text(
        string='Preview',
        readonly=True
    )
    result_message = fields.Text(
        string='Result',
        readonly=True
    )

    @api.onchange('file')
    def _onchange_file(self):
        """Preview the first few lines of the uploaded file"""
        if not self.file:
            self.preview_lines = ''
            return

        try:
            content = base64.b64decode(self.file).decode('utf-8')
            lines = content.split('\n')[:6]  # First 5 lines + header
            self.preview_lines = '\n'.join(lines)
        except Exception as e:
            self.preview_lines = f'Error reading file: {e}'

    def action_download_template(self):
        """Download a CSV template"""
        template_content = (
            'property_ref,certification_type_code,certificate_number,issue_date,expiry_date,issuer,notes\n'
            'PROP001,GSC,GAS-2024-001,2024-01-15,2025-01-14,British Gas,Annual gas safety check\n'
            'PROP002,EICR,ELEC-2024-001,2024-02-01,2029-01-31,ABC Electrical,5-year electrical inspection\n'
        )
        
        attachment = self.env['ir.attachment'].create({
            'name': 'certificate_upload_template.csv',
            'type': 'binary',
            'datas': base64.b64encode(template_content.encode('utf-8')),
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_upload(self):
        """Process the uploaded CSV file"""
        self.ensure_one()

        if not self.file:
            raise UserError(_('Please upload a CSV file'))

        try:
            content = base64.b64decode(self.file).decode('utf-8')
        except Exception as e:
            raise UserError(_('Error reading file: %s') % str(e))

        reader = csv.DictReader(io.StringIO(content))
        
        created = 0
        updated = 0
        skipped = 0
        errors = []

        Property = self.env['property_fielder.property']
        CertType = self.env['property_fielder.certification.type']
        Cert = self.env['property_fielder.property.certification']

        for row_num, row in enumerate(reader, start=2):
            try:
                # Find property
                prop = Property.search([
                    '|',
                    ('name', '=', row.get('property_ref', '').strip()),
                    ('uprn', '=', row.get('property_ref', '').strip())
                ], limit=1)
                if not prop:
                    raise ValidationError(f"Property not found: {row.get('property_ref')}")

                # Find certification type
                cert_type = CertType.search([
                    ('code', '=', row.get('certification_type_code', '').strip())
                ], limit=1)
                if not cert_type:
                    raise ValidationError(f"Certification type not found: {row.get('certification_type_code')}")

                # Parse dates
                issue_date = datetime.strptime(row.get('issue_date', '').strip(), '%Y-%m-%d').date()
                expiry_date = datetime.strptime(row.get('expiry_date', '').strip(), '%Y-%m-%d').date()

                # Check for existing certificate
                existing = Cert.search([
                    ('property_id', '=', prop.id),
                    ('certification_type_id', '=', cert_type.id),
                    ('certificate_number', '=', row.get('certificate_number', '').strip())
                ], limit=1)

                vals = {
                    'property_id': prop.id,
                    'certification_type_id': cert_type.id,
                    'certificate_number': row.get('certificate_number', '').strip(),
                    'issue_date': issue_date,
                    'expiry_date': expiry_date,
                    'issuer': row.get('issuer', '').strip(),
                    'notes': row.get('notes', '').strip(),
                }

                if existing:
                    if self.update_existing:
                        existing.write(vals)
                        updated += 1
                    else:
                        skipped += 1
                else:
                    Cert.create(vals)
                    created += 1

            except Exception as e:
                if self.skip_errors:
                    errors.append(f"Row {row_num}: {str(e)}")
                    skipped += 1
                else:
                    raise UserError(_('Error on row %d: %s') % (row_num, str(e)))

        # Build result message
        message = _('Upload complete:\n- Created: %d\n- Updated: %d\n- Skipped: %d') % (created, updated, skipped)
        if errors:
            message += _('\n\nErrors:\n') + '\n'.join(errors[:20])
            if len(errors) > 20:
                message += f'\n... and {len(errors) - 20} more errors'

        self.result_message = message

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Upload Complete'),
                'message': _('%d certificates created, %d updated, %d skipped') % (created, updated, skipped),
                'type': 'success' if not errors else 'warning',
                'sticky': True,
            }
        }

