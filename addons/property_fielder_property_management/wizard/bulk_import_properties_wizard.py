# -*- coding: utf-8 -*-
import base64
import csv
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BulkImportPropertiesWizard(models.TransientModel):
    """Wizard for bulk importing properties from CSV.
    
    Expected CSV format:
    name, street, city, postcode, property_type, bedrooms, bathrooms, owner_name, owner_email
    """
    _name = 'property_fielder.bulk.import.properties.wizard'
    _description = 'Bulk Import Properties Wizard'

    file = fields.Binary(
        string='CSV File',
        required=True,
        help='Upload a CSV file with property data'
    )
    filename = fields.Char(string='Filename')

    # Options
    update_existing = fields.Boolean(
        string='Update Existing Properties',
        default=False,
        help='If checked, existing properties (matched by UPRN or name+postcode) will be updated'
    )
    skip_errors = fields.Boolean(
        string='Skip Rows with Errors',
        default=True,
        help='Continue processing even if some rows have errors'
    )
    create_owners = fields.Boolean(
        string='Create Missing Owners',
        default=True,
        help='Create new contacts for owners not found in the system'
    )

    # Results
    preview_lines = fields.Text(string='Preview', readonly=True)
    result_message = fields.Text(string='Result', readonly=True)

    @api.onchange('file')
    def _onchange_file(self):
        """Preview the first few lines of the uploaded file"""
        if not self.file:
            self.preview_lines = ''
            return
        try:
            content = base64.b64decode(self.file).decode('utf-8')
            lines = content.split('\n')[:6]
            self.preview_lines = '\n'.join(lines)
        except Exception as e:
            self.preview_lines = f'Error reading file: {e}'

    def action_download_template(self):
        """Download a CSV template"""
        template_content = (
            'name,street,city,postcode,property_type,bedrooms,bathrooms,floor_area_sqm,'
            'owner_name,owner_email,uprn,epc_rating,tenure_type\n'
            '123 High Street,123 High Street,London,SW1A 1AA,house,3,2,120,'
            'John Smith,john@example.com,100023456789,C,freehold\n'
            'Flat 1 Oak House,1 Oak Road,Manchester,M1 1AA,flat,2,1,65,'
            'Jane Doe,jane@example.com,100023456790,B,leasehold\n'
        )
        
        attachment = self.env['ir.attachment'].create({
            'name': 'property_import_template.csv',
            'type': 'binary',
            'datas': base64.b64encode(template_content.encode('utf-8')),
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_import(self):
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
        Partner = self.env['res.partner']

        for row_num, row in enumerate(reader, start=2):
            try:
                # Find or create owner
                owner = None
                owner_email = row.get('owner_email', '').strip()
                owner_name = row.get('owner_name', '').strip()
                
                if owner_email:
                    owner = Partner.search([('email', '=', owner_email)], limit=1)
                if not owner and owner_name:
                    owner = Partner.search([('name', '=', owner_name)], limit=1)
                
                if not owner and self.create_owners and owner_name:
                    owner = Partner.create({
                        'name': owner_name,
                        'email': owner_email,
                        'is_company': False,
                    })

                # Check for existing property
                uprn = row.get('uprn', '').strip()
                name = row.get('name', '').strip()
                postcode = row.get('postcode', '').strip()
                
                existing = None
                if uprn:
                    existing = Property.search([('uprn', '=', uprn)], limit=1)
                if not existing and name and postcode:
                    existing = Property.search([
                        ('name', '=', name),
                        ('postcode', '=', postcode)
                    ], limit=1)

                # Build property values
                vals = {
                    'name': name,
                    'street': row.get('street', '').strip(),
                    'city': row.get('city', '').strip(),
                    'postcode': postcode,
                    'property_type': row.get('property_type', 'house').strip().lower(),
                    'bedrooms': int(row.get('bedrooms', 0) or 0),
                    'bathrooms': int(row.get('bathrooms', 0) or 0),
                    'floor_area_sqm': float(row.get('floor_area_sqm', 0) or 0),
                    'uprn': uprn,
                    'epc_rating': row.get('epc_rating', '').strip().upper() or False,
                    'tenure_type': row.get('tenure_type', '').strip().lower() or False,
                }
                if owner:
                    vals['partner_id'] = owner.id

                if existing:
                    if self.update_existing:
                        existing.write(vals)
                        updated += 1
                    else:
                        skipped += 1
                else:
                    Property.create(vals)
                    created += 1

            except Exception as e:
                if self.skip_errors:
                    errors.append(f"Row {row_num}: {str(e)}")
                    skipped += 1
                else:
                    raise UserError(_('Error on row %d: %s') % (row_num, str(e)))

        # Build result message
        message = _('Import complete:\n- Created: %d\n- Updated: %d\n- Skipped: %d') % (created, updated, skipped)
        if errors:
            message += _('\n\nErrors:\n') + '\n'.join(errors[:20])
            if len(errors) > 20:
                message += f'\n... and {len(errors) - 20} more errors'

        self.result_message = message

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Import Complete'),
                'message': _('%d properties created, %d updated, %d skipped') % (created, updated, skipped),
                'type': 'success' if not errors else 'warning',
                'sticky': True,
            }
        }

