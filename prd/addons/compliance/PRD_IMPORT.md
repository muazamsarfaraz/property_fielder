# PRD: Property Fielder Import

**Addon Name:** `property_fielder_import`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Feature (Layer 2)  
**Phase:** Phase 1 (Core Compliance)  
**Effort:** 15 days  

---

## 1. Overview

Data import wizard for client onboarding - essential for testing with real data.

### 1.1 Purpose
Enable bulk import of properties, certifications, and historical data from client spreadsheets and legacy systems.

### 1.2 Target Users
- Implementation Consultants
- System Administrators
- Compliance Managers

### 1.3 Business Value
- Cannot test or deploy without real data
- Reduces onboarding time from weeks to days
- Handles legacy data migration automatically

---

## 2. Dependencies

```python
depends = [
    'base',
    'contacts',  # For res.partner validation
    'queue_job',  # OCA async processing - REQUIRED
    'property_fielder_property_management',
]

external_dependencies = {
    'python': ['openpyxl', 'pandas'],  # Robust Excel/CSV parsing
}
```

---

## 3. Data Models

### 3.1 `property_fielder.import.batch`
Import batch tracking.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Batch reference |
| `import_type` | Selection | property/certification/tenant/contractor |
| `file` | Binary | Uploaded file (CSV/Excel) |
| `filename` | Char | Original filename |
| `state` | Selection | draft/mapping/validating/importing/completed/failed |
| `total_rows` | Integer | Total rows in file |
| `imported_rows` | Integer | Successfully imported |
| `failed_rows` | Integer | Failed rows |
| `mapping_id` | Many2one → import.mapping.template | Mapping template |
| `log_ids` | One2many → import.log | Import log entries |
| `dry_run` | Boolean | Preview mode (no commit) |
| `created_by` | Many2one → res.users | Who initiated |
| `date_format` | Selection | **DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD** |
| `encoding` | Selection | **utf-8, latin-1, cp1252** |
| `delimiter` | Selection | **comma, semicolon, tab, pipe** |
| `error_file` | Binary | **Exported error CSV** |
| `error_filename` | Char | **Error file name** |

### 3.2 `property_fielder.import.mapping.template`
Column mapping configuration.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Template name |
| `import_type` | Selection | property/certification/tenant/contractor |
| `mapping_ids` | One2many → import.mapping.line | Column mappings |
| `is_default` | Boolean | Default for type |

### 3.3 `property_fielder.import.mapping.line`
Individual column mapping.

| Field | Type | Description |
|-------|------|-------------|
| `template_id` | Many2one → mapping.template | Parent template |
| `source_column` | Char | Column name in file |
| `target_field_id` | Many2one → ir.model.fields | **Dynamic field selection** |
| `transformation` | Selection | none/date_parse/uppercase/etc |
| `default_value` | Char | Default if empty |
| `is_required` | Boolean | Must have value |
| `delimiter` | Char | **Delimiter for One2many/Tags (e.g., ";" to split "Gas;Electric;HMO")** |
| `search_domain` | Char | **Domain filter for relational lookup (e.g., "[('is_owner','=',True)]")** |
| `value_mapping_ids` | One2many → import.value.mapping | **Value mappings for dropdowns** |

### 3.3.1 `property_fielder.import.value.mapping`
Value mapping for Selection/Many2one fields (e.g., "Flat" → "flat", "House" → "house").

| Field | Type | Description |
|-------|------|-------------|
| `mapping_line_id` | Many2one → import.mapping.line | Parent mapping line |
| `source_value` | Char | Value in source file (e.g., "Flat", "FLAT", "Apartment") |
| `target_value` | Char | Odoo value (e.g., "flat") |
| `target_record_id` | Integer | For Many2one: target record ID |
| `target_xml_id` | Char | **External ID for env portability (e.g., "base.uk")** |
| `target_lookup_field` | Char | **Field to search by (e.g., "code" instead of ID)** |
| `is_default` | Boolean | Use as default for unmatched values |

```python
class ImportValueMapping(models.Model):
    _name = 'property_fielder.import.value.mapping'
    _description = 'Import Value Mapping'

    mapping_line_id = fields.Many2one(
        'property_fielder.import.mapping.line',
        required=True,
        ondelete='cascade'
    )
    source_value = fields.Char(required=True, help="Value in source file")
    target_value = fields.Char(help="For Selection fields: internal value")
    target_record_id = fields.Integer(help="For Many2one fields: record ID")
    is_default = fields.Boolean(help="Use as default for unmatched values")

    _sql_constraints = [
        ('unique_source_value', 'UNIQUE(mapping_line_id, source_value)',
         'Source value must be unique per mapping line')
    ]
```

### 3.4 `property_fielder.import.validation.rule`
Custom validation rules.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Rule name |
| `import_type` | Selection | property/certification/etc |
| `field` | Char | Field to validate |
| `rule_type` | Selection | regex/range/lookup/unique |
| `rule_value` | Char | Rule configuration |
| `error_message` | Char | Error message on failure |

### 3.5 `property_fielder.import.log`

Row-level import log.

**OPTIMIZATION:** Only store `source_data` for **failed** rows to prevent database bloat on large imports.

| Field | Type | Description |
|-------|------|-------------|
| `batch_id` | Many2one → import.batch | Parent batch |
| `row_number` | Integer | Row in source file |
| `status` | Selection | success/warning/error/skipped |
| `message` | Text | Log message |
| `source_data` | Text | **Original row data (JSON) - only stored if status != success** |
| `record_id` | Integer | Created/updated record ID |
| `record_model` | Char | Created record model |
| `operation` | Selection | **create/update/skip** |
| `corrected_data` | Text | **User-corrected data (JSON) for re-import** |

```python
class ImportLog(models.Model):
    _name = 'property_fielder.import.log'

    @api.model_create_multi
    def create(self, vals_list):
        """Optimize: Only store source_data for non-success rows."""
        for vals in vals_list:
            if vals.get('status') == 'success':
                vals.pop('source_data', None)  # Don't store for success
        return super().create(vals_list)
```

### 3.6 `property_fielder.import.relational.lookup`

**Relational field lookup configuration.**

| Field | Type | Description |
|-------|------|-------------|
| `mapping_line_id` | Many2one → mapping.line | Parent mapping line |
| `target_model` | Char | Model to search (e.g. 'res.partner') |
| `search_field` | Char | Field to search (e.g. 'email') |
| `create_if_missing` | Boolean | Auto-create if not found |
| `default_values` | Text | JSON default values for creation |
| `multiple_match_action` | Selection | first/error/skip |

---

## 4. Key Features

### 4.1 File Upload & Preview
- CSV and Excel (XLSX) support
- Preview first N rows before import
- Auto-detect column headers
- Handle various date formats

### 4.2 Column Mapping
- Smart auto-mapping by column name
- Save mapping templates for reuse
- Handle multiple column formats
- Default values for missing columns

### 4.3 Validation
- UPRN duplicate detection
- Postcode format validation
- Date range validation
- Required field checks
- Custom validation rules

### 4.4 Import Types

| Type | Fields | Notes |
|------|--------|-------|
| **Properties** | address, postcode, UPRN, owner, type | Creates property_fielder.property |
| **Certifications** | property ref, type, issue date, expiry | Links to existing properties |
| **Tenants** | name, email, phone, property ref | Creates contacts, links to property |
| **Contractors** | name, trades, accreditations | Creates contractor records |

### 4.5 Dry Run Mode
- Preview what will be created
- Show validation errors without committing
- Generate import report before commit

### 4.6 Idempotency (Update vs Create)

- **UPRN matching**: If UPRN exists, update property
- **Certificate number matching**: Update existing cert
- **Email matching**: Update existing contact
- `operation` field tracks: create/update/skip
- Re-import same file = no duplicates

### 4.7 Async Processing (queue_job)

- Large imports (>100 rows) processed asynchronously
- Progress tracking in UI
- Email notification on completion
- Background workers for performance
- Timeout handling for large files

### 4.8 Relational Lookup

- Owner lookup by email/name
- Property lookup by UPRN/address
- Create missing records option
- Handle multiple matches (first/error/skip)

### 4.9 Error CSV Export

**Critical for real-world usage:** Export failed rows as CSV for correction and re-import.

```python
class ImportBatch(models.Model):
    _inherit = 'property_fielder.import.batch'

    error_file = fields.Binary(string='Error CSV', readonly=True)
    error_filename = fields.Char()

    def action_export_errors(self):
        """Export failed rows as CSV for correction and re-import."""
        self.ensure_one()
        failed_logs = self.log_ids.filtered(lambda l: l.status == 'error')
        if not failed_logs:
            raise UserError("No errors to export")

        output = io.StringIO()
        writer = csv.writer(output)

        # Get original headers from first row
        first_row = json.loads(failed_logs[0].source_data)
        headers = list(first_row.keys()) + ['_error_message', '_row_number']
        writer.writerow(headers)

        for log in failed_logs:
            row_data = json.loads(log.source_data)
            row = [row_data.get(h, '') for h in list(first_row.keys())]
            row.extend([log.message, log.row_number])
            writer.writerow(row)

        self.error_file = base64.b64encode(output.getvalue().encode('utf-8'))
        self.error_filename = f'errors_{self.name}_{fields.Date.today()}.csv'

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/error_file/{self.error_filename}?download=true',
            'target': 'self',
        }
```

**Re-import Corrected Errors:**

```python
def action_reimport_corrected(self, corrected_file):
    """Re-import corrected error rows."""
    # Parse corrected CSV
    # Match by _row_number to original log entries
    # Re-validate and import only corrected rows
    # Update log entries with new status
    pass
```

### 4.9 Legacy Document Processor (Future)

- OCR for scanned certificate PDFs
- AI extraction of dates and reference numbers
- Auto-create certification records from PDFs

---

## 5. Technical Implementation

### 5.1 Async Job Processing

```python
from odoo.addons.queue_job.job import job

class ImportBatch(models.Model):
    _inherit = 'property_fielder.import.batch'

    @job(channel='root.import')
    def process_import_async(self):
        """Process import in background job."""
        for row in self._get_rows():
            self._process_row(row)
        self.state = 'completed'
        self._send_completion_email()
```

### 5.2 Idempotency Logic

```python
def _find_existing_record(self, row_data):
    """Find existing record by unique key."""
    if self.import_type == 'property':
        return self.env['property_fielder.property'].search([
            ('uprn', '=', row_data.get('uprn'))
        ], limit=1)
    # ... other types
```

---

## 6. Wizard Views

### 5.1 Import Wizard Steps
1. **Upload** - Select file and import type
2. **Preview** - See first rows, adjust settings
3. **Map** - Column to field mapping
4. **Validate** - Run validation, show errors
5. **Import** - Execute import (or dry run)
6. **Report** - Summary with success/failure counts

---

## 6. Integration Points

| System | Integration |
|--------|-------------|
| Property Management | Creates property records |
| Certifications | Creates certification records |
| Contacts | Creates tenant/owner contacts |
| Field Service | Links imported data to jobs |

---

## 7. GDPR Data Retention

### 7.1 Automatic Cleanup Cron

```python
class ImportBatch(models.Model):
    _inherit = 'property_fielder.import.batch'

    expiry_date = fields.Date(
        default=lambda self: fields.Date.today() + timedelta(days=30)
    )

    @api.model
    def _cron_purge_import_data(self):
        """GDPR: Auto-delete source files and PII after 30 days."""
        expired = self.search([
            ('expiry_date', '<', fields.Date.today()),
            ('state', 'in', ['completed', 'failed']),
        ])
        for batch in expired:
            # Clear source file (contains PII)
            batch.file = False
            # Clear raw row data from logs
            batch.log_ids.write({'source_data': False})
```

### 7.2 Attachment Import (Binary Fields)

```python
class ImportMappingLine(models.Model):
    _inherit = 'property_fielder.import.mapping.line'

    is_attachment = fields.Boolean(
        help="If True, value is URL/path to fetch and store as ir.attachment"
    )
    attachment_folder = fields.Char(
        help="Folder path for companion ZIP file attachments"
    )
```

### 7.3 Undo/Rollback Feature

```python
class ImportBatch(models.Model):
    _inherit = 'property_fielder.import.batch'

    def action_undo_batch(self):
        """Undo entire import batch - archive all created records."""
        self.ensure_one()
        if self.state != 'completed':
            raise UserError("Can only undo completed batches")

        # Get all created records from logs
        for log in self.log_ids.filtered(lambda l: l.status == 'success' and l.operation == 'create'):
            if log.record_id and log.record_model:
                record = self.env[log.record_model].browse(log.record_id)
                if record.exists() and hasattr(record, 'active'):
                    record.active = False  # Archive instead of delete

        self.state = 'rolled_back'
        self.message_post(body="Batch import undone - all created records archived")
```

---

## 8. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **queue_job dependency** | ✅ Added |
| **contacts dependency** | ✅ Added |
| **external_dependencies (openpyxl, pandas)** | ✅ Added |
| **Dynamic field mapping (ir.model.fields)** | ✅ Fixed |
| Relational lookup logic | ✅ Complete |
| Idempotency (Update vs Create) | ✅ Complete |
| Async processing (queue_job) | ✅ Complete |
| **GDPR cleanup cron** | ✅ Added |
| **Attachment import** | ✅ Added |
| Import types defined | ✅ Complete |
| Validation rules specified | ✅ Complete |
| Wizard flow clear | ✅ Complete |
| **Value Mapping for dropdowns** | ✅ Added |
| **Error CSV Export** | ✅ Added |
| **Date format config** | ✅ Added |
| **Encoding/delimiter config** | ✅ Added |
| **Re-import corrected errors** | ✅ Added |
| **One2many delimiter handling** | ✅ Added |
| **Search domain for relational lookup** | ✅ Added |
| **target_xml_id for env portability** | ✅ Added |
| **Log optimization (only store failed)** | ✅ Added |
| **Undo/Rollback batch** | ✅ Added |
| **Overall** | ✅ Build Ready (90%+) |

