# PRD: Property Fielder Property Documents

**Addon Name:** `property_fielder_property_documents`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase B (Financial & Compliance)  
**Effort:** 30-40 hours  

---

## 1. Overview

Document repository with version control and e-signatures.

### 1.1 Purpose
Centralized document management for all property-related documents including tenancy agreements, certificates, inventories, and correspondence.

### 1.2 Target Users
- Property Managers
- Compliance Managers
- Landlords
- Tenants (read access)

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for document tracking
    'portal',  # Portal access for tenants/owners
    'web',  # PDF viewer widget
    'property_fielder_property_management',
    # Note: 'documents' is Odoo Enterprise only
    # Community version uses ir.attachment directly
]
```

**Note:** The `documents` module is **Odoo Enterprise only**. For Community edition, this addon uses `ir.attachment` directly with custom folder/tag models.

---

## 3. Data Models

### 3.1 `property_fielder.document`

**Inherits mail.thread for audit trail.**

```python
class PropertyDocument(models.Model):
    _name = 'property_fielder.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Document name |
| `property_id` | Many2one → property | Related property |
| `tenancy_id` | Many2one → tenancy | Related tenancy |
| `document_type_id` | Many2one → document.type | **Dynamic document type** |
| `category` | Selection | legal/compliance/financial/general |
| `attachment_id` | Many2one → ir.attachment | **Document stored as attachment** |
| `filename` | Char | Original filename |
| `file_size` | Integer | File size (bytes) |
| `mime_type` | Char | MIME type |
| `version` | Integer | Version number |
| `is_current` | Boolean | Current version |
| `previous_version_id` | Many2one → self | Previous version |
| `history_ids` | One2many → self | **Version history** |
| `created_date` | Datetime | Upload date |
| `created_by` | Many2one → res.users | Uploaded by |
| `issue_date` | Date | **Document issue date (e.g., CP12 check date)** |
| `expiry_date` | Date | Document expiry (if applicable) |
| `is_portal_visible` | Boolean | **Visible to tenants on portal** |
| `is_right_to_rent` | Boolean | **Used for Right to Rent check** |
| `signature_required` | Boolean | Requires e-signature |
| `signature_ids` | Many2many → e.signature | Signatures |
| `signed` | Boolean | Fully signed |
| `template_id` | Many2one → ir.actions.report | **QWeb template used for generation (enables regeneration)** |
| `source_record_ref` | Reference | **Source record for regeneration (e.g., tenancy)** |

### 3.2 `property_fielder.document.type`

**Dynamic document types (configurable by admin):**

```python
class DocumentType(models.Model):
    _name = 'property_fielder.document.type'
    _description = 'Document Type'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    default_validity_days = fields.Integer(
        help="Default validity period (e.g., 365 for Gas Safety)"
    )
    is_statutory_requirement = fields.Boolean(
        help="Required for compliance (Gas, EICR, EPC)"
    )
    required_for_move_in = fields.Boolean(
        help="Must be provided before tenancy starts"
    )
    updates_property_field = fields.Char(
        help="Property field to update on upload (e.g., 'gas_safety_expiry')"
    )
    portal_visible_default = fields.Boolean(
        help="Default visibility on tenant portal"
    )
    retention_years = fields.Integer(
        default=6,
        help="GDPR: Years to retain after tenancy ends"
    )
```

**Seed Data:**

| Code | Name | Validity | Statutory | Move-in | Updates Field |
|------|------|----------|-----------|---------|---------------|
| `GAS_CERT` | Gas Safety Certificate | 365 | ✅ | ✅ | `gas_safety_expiry` |
| `EICR` | Electrical Report | 1825 | ✅ | ✅ | `eicr_expiry` |
| `EPC` | Energy Performance | 3650 | ✅ | ✅ | `epc_expiry` |
| `AST` | Tenancy Agreement | - | ✅ | ✅ | - |
| `DEPOSIT_CERT` | Deposit Certificate | - | ✅ | ✅ | - |
| `HOW_TO_RENT` | How to Rent Guide | - | ✅ | ✅ | - |

### 3.1.1 How to Rent Version Logic

**UK Requirement:** The "How to Rent" guide version must be current at tenancy start date.

```python
class PropertyDocument(models.Model):
    _inherit = 'property_fielder.document'

    how_to_rent_version = fields.Char(
        string='How to Rent Version',
        help="Version of How to Rent guide (e.g., 'October 2023')"
    )

    @api.constrains('document_type_id', 'tenancy_id', 'how_to_rent_version')
    def _check_how_to_rent_version(self):
        """Ensure How to Rent version is current at tenancy start."""
        for rec in self:
            if rec.document_type_id.code == 'HOW_TO_RENT' and rec.tenancy_id:
                # Get current version from config
                current_version = self.env['ir.config_parameter'].sudo().get_param(
                    'property_fielder.how_to_rent_current_version', 'October 2023'
                )
                current_version_date = self.env['ir.config_parameter'].sudo().get_param(
                    'property_fielder.how_to_rent_version_date', '2023-10-01'
                )
                tenancy_start = rec.tenancy_id.start_date

                # If tenancy started after version date, must use current version
                if tenancy_start >= fields.Date.from_string(current_version_date):
                    if rec.how_to_rent_version != current_version:
                        raise ValidationError(
                            f"How to Rent guide must be version '{current_version}' "
                            f"for tenancies starting after {current_version_date}."
                        )
```

| `INVENTORY` | Check-in Inventory | - | ❌ | ❌ | - |
| `FIRE_RA` | Fire Risk Assessment | 365 | ✅ (HMO) | ❌ | `fire_ra_expiry` |

### 3.2 `property_fielder.e.signature`
E-signature record.

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | Many2one → document | Document |
| `signer_id` | Many2one → res.partner | Signer |
| `signer_role` | Selection | tenant/landlord/guarantor/witness |
| `signed_date` | Datetime | Signature date |
| `signature_image` | Binary | Signature image |
| `ip_address` | Char | IP address |
| `ip_address_geo` | Char | **Geolocation from IP (country/city for audit)** |
| `user_agent` | Char | **Browser user agent string** |
| `email_verified` | Boolean | Email verified |
| `certificate` | Binary | Signing certificate |
| `witness_id` | Many2one → res.partner | **Witness (required for Deeds)** |
| `witness_signature_image` | Binary | **Witness signature** |
| `witness_signed_date` | Datetime | **Witness signature date** |
| `is_deed` | Boolean | **Document is a Deed (requires witness)** |

### 3.2.1 Deed Witness Requirements

**UK Law:** Tenancy agreements over 3 years must be executed as Deeds, requiring witness signatures.

```python
class ESignature(models.Model):
    _name = 'property_fielder.e.signature'

    @api.constrains('document_id', 'witness_id')
    def _check_deed_witness(self):
        """Deeds require witness signatures."""
        for rec in self:
            if rec.is_deed and not rec.witness_id:
                raise ValidationError(
                    "Deeds (tenancies over 3 years) require a witness signature. "
                    "The witness must be independent (not a party to the agreement)."
                )

    @api.onchange('document_id')
    def _onchange_document_deed(self):
        """Auto-set is_deed based on tenancy length."""
        if self.document_id.tenancy_id:
            tenancy = self.document_id.tenancy_id
            if tenancy.fixed_term_months and tenancy.fixed_term_months > 36:
                self.is_deed = True
```

### 3.3 Document Types

| Type | Description |
|------|-------------|
| `tenancy_agreement` | Tenancy agreement |
| `gas_certificate` | Gas Safety Certificate (CP12) |
| `eicr` | Electrical Installation Report |
| `epc` | Energy Performance Certificate |
| `fire_risk` | Fire Risk Assessment |
| `inventory` | Check-in inventory |
| `checkout_report` | Check-out report |
| `deposit_certificate` | Deposit protection certificate |
| `how_to_rent` | How to Rent Guide |
| `correspondence` | Letters, notices |
| `photo_report` | Photo evidence report |

---

## 4. Key Features

### 4.1 Document Upload
- Drag-drop upload
- Bulk upload
- Auto-categorization
- Thumbnail generation (PDFs)

### 4.2 Version Control
- Automatic versioning
- Version history
- Rollback capability
- Diff viewing (future)

### 4.3 E-Signatures
- Request signatures via email
- Multiple signers
- Audit trail
- Certificate generation

### 4.4 OCR Processing (Future)
- Extract text from scanned PDFs
- Auto-extract dates
- Auto-categorize documents

### 4.5 Access Control
- Role-based access
- Tenant access to relevant docs only
- Expiring share links

### 4.6 Expiry Tracking & Compliance Write-back

```python
class PropertyDocument(models.Model):
    _inherit = 'property_fielder.document'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._update_property_compliance()
        return records

    def _update_property_compliance(self):
        """Auto-update property compliance fields on document upload."""
        if not self.document_type_id.updates_property_field:
            return
        field_name = self.document_type_id.updates_property_field
        if hasattr(self.property_id, field_name):
            setattr(self.property_id, field_name, self.expiry_date)
            self.property_id.message_post(
                body=f"Compliance updated: {self.document_type_id.name} expires {self.expiry_date}"
            )
```

### 4.7 Document Generation (QWeb Templates)

**Generate documents from Odoo data (ASTs, Notices, Statements):**

```python
class PropertyDocument(models.Model):
    _inherit = 'property_fielder.document'

    @api.model
    def generate_from_template(self, template_ref, record, document_type_code):
        """Generate PDF document from QWeb template."""
        template = self.env.ref(template_ref)
        pdf_content = self.env['ir.actions.report']._render_qweb_pdf(
            template.id, [record.id]
        )[0]

        attachment = self.env['ir.attachment'].create({
            'name': f'{document_type_code}_{record.name}.pdf',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
        })

        doc_type = self.env['property_fielder.document.type'].search([
            ('code', '=', document_type_code)
        ], limit=1)

        return self.create({
            'name': f'{doc_type.name} - {record.name}',
            'property_id': record.property_id.id if hasattr(record, 'property_id') else False,
            'tenancy_id': record.id if record._name == 'property_fielder.tenancy' else False,
            'document_type_id': doc_type.id,
            'attachment_id': attachment.id,
            'issue_date': fields.Date.today(),
        })

# Example: Generate Tenancy Agreement
# self.env['property_fielder.document'].generate_from_template(
#     'property_fielder_property_documents.report_tenancy_agreement',
#     tenancy,
#     'AST'
# )
```

### 4.8 Digital Acceptance (Simplified E-Signature)

**Phase 1: Token-based acceptance (not full e-signature):**

```python
class PropertyDocument(models.Model):
    _inherit = 'property_fielder.document'

    acceptance_token = fields.Char()
    acceptance_url = fields.Char(compute='_compute_acceptance_url')

    def _compute_acceptance_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if rec.acceptance_token:
                rec.acceptance_url = f"{base_url}/document/accept/{rec.acceptance_token}"
            else:
                rec.acceptance_url = False

    def action_send_for_acceptance(self, partner_id):
        """Send document for digital acceptance."""
        self.acceptance_token = secrets.token_urlsafe(32)
        template = self.env.ref(
            'property_fielder_property_documents.email_document_acceptance'
        )
        template.send_mail(self.id, force_send=True)

# Controller: /document/accept/<token>
# Logs: IP, Timestamp, User-Agent
# Creates: property_fielder.e.signature record
# Sufficient for UK ASTs (Electronic Communications Act 2000)
```

### 4.9 Proof of Service

**UK Legal Requirement:** Certain documents must be served with proof of delivery.

```python
class DocumentService(models.Model):
    _name = 'property_fielder.document.service'
    _description = 'Proof of Service'

    document_id = fields.Many2one('property_fielder.document', required=True)
    recipient_id = fields.Many2one('res.partner', required=True)
    service_method = fields.Selection([
        ('email', 'Email'),
        ('post', 'First Class Post'),
        ('recorded', 'Recorded Delivery'),
        ('hand', 'Hand Delivery'),
    ])
    service_date = fields.Datetime()
    tracking_reference = fields.Char(string='Tracking/Reference')
    proof_attachment_id = fields.Many2one('ir.attachment', string='Proof')

    # Email tracking
    email_opened = fields.Boolean()
    email_opened_date = fields.Datetime()

    # Deemed served date (post = +2 working days)
    deemed_served_date = fields.Date(compute='_compute_deemed_served')
```

---

## 5. Technical Notes

### 5.1 Storage Architecture

- Uses `ir.attachment` for document storage (not Binary field)
- Supports Odoo S3/cloud storage backends
- Thumbnail generation via LibreOffice/Ghostscript

### 5.2 PDF Viewer Widget

**In-form PDF viewing to avoid constant downloading:**

```xml
<!-- views/property_document_views.xml -->
<field name="attachment_id" widget="pdf_viewer" options="{'height': 600}"/>
```

**Note:** Requires `web_widget_pdf_viewer` community module or custom widget:

```javascript
// static/src/js/pdf_viewer_widget.js
import { registry } from "@web/core/registry";
import { Component, xml } from "@odoo/owl";

class PdfViewerField extends Component {
    static template = xml`
        <iframe t-att-src="pdfUrl" width="100%" height="600px"/>
    `;
    get pdfUrl() {
        return `/web/content/${this.props.value}?download=false`;
    }
}
registry.category("fields").add("pdf_viewer", PdfViewerField);
```

### 5.3 Expected Signers Logic

**Define who should sign a document based on tenancy:**

```python
class PropertyDocument(models.Model):
    _inherit = 'property_fielder.document'

    expected_signer_ids = fields.Many2many(
        'res.partner', string='Expected Signers',
        compute='_compute_expected_signers', store=True
    )
    all_signed = fields.Boolean(compute='_compute_all_signed', store=True)

    @api.depends('tenancy_id', 'document_type_id')
    def _compute_expected_signers(self):
        """Determine who should sign based on document type."""
        for rec in self:
            signers = self.env['res.partner']
            if rec.tenancy_id and rec.document_type_id:
                if rec.document_type_id.code in ['AST', 'RENEWAL']:
                    # All tenants must sign tenancy agreements
                    signers = rec.tenancy_id.tenant_ids
                    # Guarantor if present
                    if rec.tenancy_id.guarantor_id:
                        signers |= rec.tenancy_id.guarantor_id
                elif rec.document_type_id.code == 'INVENTORY':
                    # Lead tenant signs inventory
                    signers = rec.tenancy_id.lead_tenant_id
            rec.expected_signer_ids = signers

    @api.depends('signature_ids', 'expected_signer_ids')
    def _compute_all_signed(self):
        """Check if all expected signers have signed."""
        for rec in self:
            if not rec.expected_signer_ids:
                rec.all_signed = True
            else:
                signed_partners = rec.signature_ids.mapped('partner_id')
                rec.all_signed = all(
                    p in signed_partners for p in rec.expected_signer_ids
                )
```

### 5.4 Portal Controller Routes

```python
class DocumentPortalController(http.Controller):

    @http.route('/my/documents', type='http', auth='user', website=True)
    def portal_documents(self, **kw):
        """List tenant's accessible documents."""
        partner = request.env.user.partner_id
        tenancies = request.env['property_fielder.tenancy'].search([
            ('tenant_ids', 'in', [partner.id])
        ])
        documents = request.env['property_fielder.document'].search([
            ('tenancy_id', 'in', tenancies.ids),
            ('is_portal_visible', '=', True),
        ])
        return request.render('property_fielder_property_documents.portal_documents', {
            'documents': documents,
        })

    @http.route('/my/documents/<int:doc_id>/download', type='http', auth='user')
    def download_document(self, doc_id, **kw):
        """Download a document (with access check)."""
        document = request.env['property_fielder.document'].browse(doc_id)
        # Access check
        partner = request.env.user.partner_id
        if partner not in document.tenancy_id.tenant_ids:
            return request.redirect('/my/documents?error=access_denied')

        return request.make_response(
            base64.b64decode(document.attachment_id.datas),
            headers=[
                ('Content-Type', document.mime_type),
                ('Content-Disposition', f'attachment; filename="{document.filename}"'),
            ]
        )
```

### 5.5 GDPR Compliance

- Document retention policies
- Tenant data portability
- Right to erasure (cascade delete with tenancy)
- Access logging

### 5.6 GDPR Retention Cron Job

**Hard-delete documents after retention period (especially Right to Rent IDs):**

```xml
<!-- data/ir_cron.xml -->
<record id="ir_cron_document_retention" model="ir.cron">
    <field name="name">Property Fielder: Document Retention Cleanup</field>
    <field name="model_id" ref="model_property_fielder_document"/>
    <field name="state">code</field>
    <field name="code">model._cron_enforce_retention()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

```python
class PropertyDocument(models.Model):
    _inherit = 'property_fielder.document'

    def _cron_enforce_retention(self):
        """Delete documents past their retention period (GDPR compliance)."""
        today = fields.Date.today()

        # Find documents with retention rules
        doc_types = self.env['property_fielder.document.type'].search([
            ('retention_years', '>', 0)
        ])

        for doc_type in doc_types:
            cutoff_date = today - relativedelta(years=doc_type.retention_years)

            # Special handling for Right to Rent (12 months after tenancy end)
            if doc_type.code == 'RIGHT_TO_RENT':
                docs = self.search([
                    ('document_type_id', '=', doc_type.id),
                    ('tenancy_id.state', '=', 'ended'),
                    ('tenancy_id.end_date', '<', today - relativedelta(months=12)),
                ])
            else:
                docs = self.search([
                    ('document_type_id', '=', doc_type.id),
                    ('created_date', '<', cutoff_date),
                ])

            for doc in docs:
                # Log before deletion
                _logger.info(f"GDPR Retention: Deleting document {doc.name} (ID: {doc.id})")
                # Delete attachment (actual file)
                if doc.attachment_id:
                    doc.attachment_id.unlink()
                # Delete document record
                doc.unlink()
```

---

## 6. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **document_type as Many2one** | ✅ Fixed |
| **issue_date field** | ✅ Added |
| **Document generation (QWeb)** | ✅ Added |
| **is_portal_visible field** | ✅ Added |
| **Digital Acceptance (Phase 1)** | ✅ Added |
| **Compliance write-back** | ✅ Added |
| **Document Type seed data** | ✅ Added |
| **mail.thread inheritance** | ✅ Added |
| **Enterprise/Community clarified** | ✅ Added |
| **Proof of Service model** | ✅ Added |
| **PDF Viewer widget** | ✅ Added |
| **Expected Signers logic** | ✅ Added |
| **Portal controller routes** | ✅ Added |
| **GDPR retention cron job** | ✅ Added |
| **Right to Rent 12-month deletion** | ✅ Added |
| **portal and web in dependencies** | ✅ Added |
| **template_id for regeneration** | ✅ Added |
| **source_record_ref for regeneration** | ✅ Added |
| **ip_address_geo on e.signature** | ✅ Added |
| **user_agent on e.signature** | ✅ Added |
| **How to Rent version logic** | ✅ Added |
| **Deed witness requirements (>3yr AST)** | ✅ Added |
| **witness_id on e.signature** | ✅ Added |
| **is_deed flag** | ✅ Added |
| Uses ir.attachment | ✅ Complete |
| Version control clear | ✅ Complete |
| E-signature workflow defined | ✅ Complete |
| Access control specified | ✅ Complete |
| GDPR compliance | ✅ Complete |
| **Overall** | ✅ Build Ready (90%+) |

