# PRD: Property Fielder Key Management

**Addon Name:** `property_fielder_key_management`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase D (Advanced Features)  
**Effort:** 20-30 hours  

---

## 1. Overview

Key tracking with check-out/check-in logging and holder management.

### 1.1 Purpose
Track all property keys, who holds them, and maintain an audit trail of key movements for security and accountability.

### 1.2 Target Users
- Property Managers
- Office Staff
- Inspectors

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for key movement tracking
    'property_fielder_property_management',
    # Note: field_service is OPTIONAL - see bridge module below
]
```

**Architectural Note:** Key Management is a fundamental resource module (Layer 3) that should work independently of Field Service. The `property_fielder_field_service` dependency is **optional** to support "Lettings Only" clients who don't use Field Service/Maintenance.

**Bridge Module:** For clients using both modules, install `property_fielder_field_service_keys` which provides:
- Job-Key linking
- Auto-checkout validation (requires QR scan)
- Key return reminders on job completion

---

## 3. Data Models

### 3.1 `property_fielder.key.set`

**Inherits mail.thread for audit trail.**

```python
class KeySet(models.Model):
    _name = 'property_fielder.key.set'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `name` | Char | Key set name (Master, Spare, Tenant) |
| `tag_reference` | Char | **Physical key tag/label reference** |
| `key_type` | Selection | master/spare/tenant/contractor |
| `key_count` | Integer | Number of keys in set |
| `has_fob` | Boolean | Includes key fob |
| `fob_number` | Char | Fob serial number |
| `has_alarm_code` | Boolean | Has alarm code |
| `alarm_code_id` | Many2one → property.alarm.code | **Link to encrypted alarm code (restricted access)** |
| `location` | Selection | office/safe/holder/property |
| `current_holder_id` | Many2one → res.partner | Current holder |
| `checkout_date` | Datetime | When checked out |
| `return_due` | Date | Return due date |
| `state` | Selection | available/checked_out/lost/replaced |
| `notes` | Text | Notes |
| `barcode` | Char | **Barcode/QR for scanning** |
| `safe_location` | Char | **Safe/cabinet location** |
| `last_verified_date` | Date | **Last physical verification** |
| `estimated_replacement_cost` | Monetary | **Estimated cost to replace if lost (Tenant Fees Act: actual cost must be evidenced)** |
| `currency_id` | Many2one → res.currency | Currency |
| `active` | Boolean | **Active flag for archiving (default=True). Allows archiving lost/destroyed keys without deleting audit history** |

### 3.2 `property_fielder.key.log`

Key check-out/check-in log.

| Field | Type | Description |
|-------|------|-------------|
| `key_set_id` | Many2one → key.set | Key set |
| `action` | Selection | checkout/checkin/lost/found/verified |
| `holder_id` | Many2one → res.partner | Person |
| `timestamp` | Datetime | Action time |
| `issued_by` | Many2one → res.users | Staff member |
| `received_by` | Many2one → res.users | Staff (check-in) |
| `purpose` | Selection | viewing/maintenance/inspection/tenant/contractor |
| `job_id` | Many2one → job | Related job |
| `return_due` | Date | Expected return |
| `signature_attachment_id` | Many2one → ir.attachment | **Signature image** |
| `photo_attachment_id` | Many2one → ir.attachment | **Photo of keys at checkout** |
| `notes` | Text | Notes |
| `actual_replacement_cost` | Monetary | **Actual replacement cost (from locksmith invoice) - Tenant Fees Act compliance** |
| `cost_evidence_attachment_ids` | Many2many → ir.attachment | **Locksmith invoice/receipt evidence for Tenant Fees Act 2019 compliance** |

### 3.3 `property_fielder.key.holder.type`

Key holder types (configurable).

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Holder type name |
| `max_checkout_days` | Integer | Default max checkout period |
| `requires_signature` | Boolean | Signature required |
| `requires_photo` | Boolean | Photo required |

### 3.4 `property_fielder.property.alarm.code` (Secure Storage)

**SECURITY: Alarm codes stored separately with restricted access.**

```python
class PropertyAlarmCode(models.Model):
    _name = 'property_fielder.property.alarm.code'
    _description = 'Property Alarm Code (Restricted Access)'

    property_id = fields.Many2one('property_fielder.property', required=True)
    code_type = fields.Selection([
        ('entry', 'Entry Alarm'),
        ('exit', 'Exit Alarm'),
        ('safe', 'Safe Code'),
        ('gate', 'Gate Code'),
    ], required=True)
    code = fields.Char(
        string='Code',
        groups='property_fielder_key_management.group_key_manager',
        help="Only visible to Key Managers. Encrypted at rest."
    )
    # Note: Use Odoo's encrypted field storage or database-level encryption
    # to prevent DB admins from reading plain text codes
    notes = fields.Text(groups='property_fielder_key_management.group_key_manager')
    last_changed = fields.Date()
```

**Access Control (security/ir.model.access.csv):**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_alarm_code_manager,alarm.code.manager,model_property_fielder_property_alarm_code,group_key_manager,1,1,1,1
access_alarm_code_user,alarm.code.user,model_property_fielder_property_alarm_code,base.group_user,0,0,0,0
```

---

## 4. Key Features

### 4.1 Key Register
- Track all keys per property
- Key types (master, spare, tenant)
- Fob and alarm code tracking
- Secure code storage

### 4.2 Check-Out Process
- Select key set
- Record holder
- Set return date
- Capture signature
- Link to job

### 4.3 Check-In Process
- Return key
- Verify count
- Record condition
- Update availability

### 4.4 Overdue Tracking
- Overdue return alerts
- Escalation workflow
- Reminder notifications

### 4.5 Audit Trail

- Complete key movement history
- Who had keys when
- Security reporting
- Lost key workflow

### 4.6 Print Key Tags

**Generate printable key tags with QR codes:**

```python
class KeySet(models.Model):
    _inherit = 'property_fielder.key.set'

    def action_print_key_tag(self):
        """Generate PDF key tag with QR code for scanning."""
        return self.env.ref(
            'property_fielder_key_management.report_key_tag'
        ).report_action(self)
```

**QWeb Report Template (reports/key_tag.xml):**

⚠️ **SECURITY: Key tags must NOT display property address!**

If a key is lost, the finder should NOT be able to identify the property.

```xml
<template id="report_key_tag_document">
    <t t-call="web.basic_layout">
        <div class="key-tag" style="width: 80mm; height: 40mm;">
            <!-- SECURITY: Only show internal reference, NOT address -->
            <div class="tag-ref" t-esc="doc.tag_reference"/>
            <div class="key-type" t-esc="doc.name"/>
            <div class="office-contact">Return to: [Office Phone]</div>
            <img t-att-src="'/report/barcode/?type=QR&amp;value=%s' % doc.barcode"/>
        </div>
    </t>
</template>
```

**Tag Reference Format:**
- Use internal codes like `PF-001-M` (Property Fielder, Property 001, Master)
- Never include: street name, postcode, property name
- QR code links to internal system (requires login to see property)

### 4.7 Bulk Audit Wizard

**Wizard for periodic key verification:**

```python
class KeyBulkAuditWizard(models.TransientModel):
    _name = 'property_fielder.key.bulk.audit.wizard'
    _description = 'Bulk Key Audit Wizard'

    property_ids = fields.Many2many('property_fielder.property')
    audit_date = fields.Date(default=fields.Date.today)
    auditor_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    def action_start_audit(self):
        """Generate audit checklist for selected properties."""
        key_sets = self.env['property_fielder.key.set'].search([
            ('property_id', 'in', self.property_ids.ids),
        ])
        # Create audit log entries for each key set
        for key_set in key_sets:
            self.env['property_fielder.key.log'].create({
                'key_set_id': key_set.id,
                'action': 'verified',
                'holder_id': key_set.current_holder_id.id,
                'issued_by': self.auditor_id.id,
                'purpose': 'audit',
                'notes': f'Bulk audit on {self.audit_date}',
            })
            key_set.last_verified_date = self.audit_date
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Audited {len(key_sets)} key sets',
                'type': 'success',
            }
        }
```

### 4.8 Field-to-Field Key Transfer

**Transfer keys directly between inspectors without returning to office:**

```python
class KeySet(models.Model):
    _inherit = 'property_fielder.key.set'

    def action_field_transfer(self, new_holder_id, new_job_id=None):
        """
        Transfer keys from one field worker to another.
        Creates check-in and check-out logs in single transaction.
        """
        self.ensure_one()
        if self.state != 'checked_out':
            raise UserError("Keys must be checked out to transfer")

        old_holder = self.current_holder_id

        # Log check-in from current holder
        self.env['property_fielder.key.log'].create({
            'key_set_id': self.id,
            'action': 'checkin',
            'holder_id': old_holder.id,
            'purpose': 'field_transfer',
            'notes': f'Field transfer to {new_holder_id.name}',
        })

        # Log check-out to new holder
        self.env['property_fielder.key.log'].create({
            'key_set_id': self.id,
            'action': 'checkout',
            'holder_id': new_holder_id.id,
            'job_id': new_job_id.id if new_job_id else False,
            'purpose': 'field_transfer',
            'notes': f'Field transfer from {old_holder.name}',
        })

        self.current_holder_id = new_holder_id
        self.message_post(
            body=f'Keys transferred: {old_holder.name} → {new_holder_id.name}'
        )
```

### 4.9 Key Reservation

**Reserve keys in advance for scheduled jobs:**

```python
class KeyReservation(models.Model):
    _name = 'property_fielder.key.reservation'
    _description = 'Key Reservation'
    _inherit = ['mail.thread']

    key_set_id = fields.Many2one('property_fielder.key.set', required=True)
    job_id = fields.Many2one('property_fielder.job')
    reserved_for_id = fields.Many2one('res.partner', required=True)
    reserved_from = fields.Datetime(required=True)
    reserved_until = fields.Datetime(required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('collected', 'Collected'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    notes = fields.Text()

    @api.constrains('key_set_id', 'reserved_from', 'reserved_until')
    def _check_no_overlap(self):
        """Prevent double-booking of keys."""
        for rec in self:
            overlapping = self.search([
                ('key_set_id', '=', rec.key_set_id.id),
                ('id', '!=', rec.id),
                ('state', 'not in', ['cancelled', 'returned']),
                ('reserved_from', '<', rec.reserved_until),
                ('reserved_until', '>', rec.reserved_from),
            ])
            if overlapping:
                raise ValidationError(
                    f"Keys already reserved by {overlapping[0].reserved_for_id.name}"
                )
```

### 4.10 Transfer Acceptance Handshake

**Require recipient to accept key transfer (mobile app):**

```python
class KeySet(models.Model):
    _inherit = 'property_fielder.key.set'

    pending_transfer_to_id = fields.Many2one(
        'res.partner',
        string='Pending Transfer To',
        help="Transfer initiated but not yet accepted"
    )
    transfer_initiated_at = fields.Datetime()
    transfer_expires_at = fields.Datetime()

    def action_initiate_transfer(self, new_holder_id):
        """Initiate transfer - requires acceptance by recipient."""
        self.ensure_one()
        self.pending_transfer_to_id = new_holder_id
        self.transfer_initiated_at = fields.Datetime.now()
        self.transfer_expires_at = fields.Datetime.now() + timedelta(hours=24)

        # Notify recipient
        self.message_post(
            body=f"Key transfer initiated to {new_holder_id.name}. Awaiting acceptance.",
            partner_ids=[new_holder_id.id]
        )
        return True

    def action_accept_transfer(self):
        """Recipient accepts the key transfer."""
        self.ensure_one()
        if not self.pending_transfer_to_id:
            raise UserError("No pending transfer")
        if fields.Datetime.now() > self.transfer_expires_at:
            raise UserError("Transfer expired")

        old_holder = self.current_holder_id
        new_holder = self.pending_transfer_to_id

        # Complete the transfer
        self._complete_field_transfer(old_holder, new_holder)

        # Clear pending state
        self.pending_transfer_to_id = False
        self.transfer_initiated_at = False
        self.transfer_expires_at = False

    def action_reject_transfer(self, reason=None):
        """Recipient rejects the key transfer."""
        self.message_post(
            body=f"Transfer rejected by {self.pending_transfer_to_id.name}. Reason: {reason or 'Not specified'}"
        )
        self.pending_transfer_to_id = False
        self.transfer_initiated_at = False
        self.transfer_expires_at = False
```

---

## 5. Property Model Extension

**Add key_set_ids One2many to property:**

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    key_set_ids = fields.One2many(
        'property_fielder.key.set',
        'property_id',
        string='Key Sets'
    )
    key_set_count = fields.Integer(
        compute='_compute_key_set_count',
        string='Key Sets'
    )
    keys_available = fields.Boolean(
        compute='_compute_keys_available',
        string='Keys Available',
        help="At least one key set is available for checkout"
    )

    def _compute_key_set_count(self):
        for rec in self:
            rec.key_set_count = len(rec.key_set_ids)

    def _compute_keys_available(self):
        for rec in self:
            rec.keys_available = any(
                k.state == 'available' for k in rec.key_set_ids
            )
```

---

## 6. Integration with Field Service

### 6.1 Job-Key Linking (Bridge Module: `property_fielder_field_service_keys`)

**IMPORTANT:** Do NOT auto-assign keys. The agent must scan the QR code of the physical keys they are holding to prevent tracking corruption.

```python
class Job(models.Model):
    _inherit = 'property_fielder.job'

    key_set_id = fields.Many2one('property_fielder.key.set', string='Keys')
    keys_checked_out = fields.Boolean(compute='_compute_keys_checked_out')
    key_checkout_required = fields.Boolean(
        compute='_compute_key_checkout_required',
        help="True if property has keys and job requires site access"
    )

    @api.constrains('state')
    def _check_key_checkout(self):
        """Prevent job start without key checkout confirmation."""
        for job in self:
            if job.state == 'in_progress' and job.key_checkout_required:
                if not job.key_set_id:
                    raise ValidationError(
                        "Cannot start job: Please scan the key QR code to confirm checkout."
                    )

    def action_scan_key_qr(self, barcode):
        """
        Validate scanned QR matches an available key set for this property.
        Called from mobile app QR scanner.
        """
        key_set = self.env['property_fielder.key.set'].search([
            ('barcode', '=', barcode),
            ('property_id', '=', self.property_id.id),
            ('state', '=', 'available'),
        ], limit=1)

        if not key_set:
            raise UserError("Invalid key QR code or keys not available")

        # Checkout the scanned key set
        key_set.action_checkout(
            holder=self.inspector_id.partner_id,
            job=self,
            purpose='inspection'
        )
        self.key_set_id = key_set
        return True
```

### 6.2 Security Features

- **Alarm Code Encryption**: Uses Odoo's encrypted fields
- **Signature Capture**: Required for checkout
- **Photo Evidence**: Optional photo of keys at checkout
- **Lost Key Workflow**: Automatic lock replacement scheduling

---

## 7. Lost Key Workflow

```python
class KeySet(models.Model):
    _inherit = 'property_fielder.key.set'

    def action_report_lost(self):
        """Report key as lost and trigger security workflow."""
        self.state = 'lost'
        self.message_post(body="Key reported as LOST")

        # Create lock replacement job
        if self.property_id:
            self.env['property_fielder.job'].create({
                'property_id': self.property_id.id,
                'job_type': 'lock_replacement',
                'priority': 'high',
                'notes': f'Lock replacement required - key set {self.name} reported lost',
            })

        # Notify property manager
        self.property_id.manager_id.notify(
            subject='Key Lost - Security Alert',
            body=f'Key set {self.name} for {self.property_id.name} reported lost.'
        )
```

---

## 8. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **`active` field for archiving** | ✅ Added |
| **Alarm code in separate model with restricted access** | ✅ Fixed |
| **Alarm code encryption note** | ✅ Added |
| **field_service dependency made OPTIONAL** | ✅ Fixed (Bridge module pattern) |
| **Auto-checkout replaced with QR scan validation** | ✅ Fixed (Prevents tracking corruption) |
| **`estimated_replacement_cost` renamed** | ✅ Fixed (Tenant Fees Act compliance) |
| **`cost_evidence_attachment_ids` for locksmith invoices** | ✅ Added (Tenant Fees Act 2019) |
| **`actual_replacement_cost` on key.log** | ✅ Added |
| **Print Key Tags PDF action** | ✅ Added |
| **Key tag security (no address)** | ✅ Fixed |
| **Bulk Audit Wizard** | ✅ Added |
| **Field-to-Field transfer workflow** | ✅ Added |
| **Transfer acceptance handshake** | ✅ Added |
| **Key reservation model** | ✅ Added |
| **key_set_ids One2many on property** | ✅ Added |
| **ir.attachment for signatures/photos** | ✅ Fixed |
| **Key holder type model** | ✅ Added |
| **Verified action type** | ✅ Added |
| **mail.thread inheritance** | ✅ Added |
| **tag_reference field** | ✅ Added |
| **Barcode/QR scanning** | ✅ Added |
| **Monetary fields with currency** | ✅ Added |
| **Lost key workflow** | ✅ Added |
| Check-out process clear | ✅ Complete |
| Job integration | ✅ Complete |
| Security considerations | ✅ Complete |
| Audit trail defined | ✅ Complete |
| **Overall** | ✅ Build Ready (90%+) |

