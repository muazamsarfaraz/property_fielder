# PRD: Property Fielder Tenant Portal

**Addon Name:** `property_fielder_tenant_portal`  
**Version:** 2.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase A (Core Operations)  
**Effort:** 60-80 hours  

---

## 1. Overview

Self-service portal for tenants to view tenancy details, report issues, and manage communications.

### 1.1 Purpose
Provide tenants with 24/7 access to their tenancy information, documents, maintenance reporting, and compliance certificates as required by UK law.

### 1.2 Target Users
- Tenants (named on AST)
- Permitted Occupiers (view-only)
- Guarantors (limited financial view)

---

## 2. Dependencies

```python
depends = [
    'base',
    'website',
    'portal',
    'mail',
    'account',  # For payment history and outstanding balance
    'property_fielder_property_leasing',
    'property_fielder_property_maintenance',
    'property_fielder_property_documents',
]
```

---

## 3. Technical Architecture

### 3.1 Portal Controllers (`controllers/main.py`)

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/my/tenancy` | GET | user | Dashboard with tenancy overview |
| `/my/tenancy/<int:tenancy_id>` | GET | user | Specific tenancy details |
| `/my/maintenance` | GET | user | List maintenance requests |
| `/my/maintenance/new` | GET/POST | user | Report new issue |
| `/my/maintenance/<int:request_id>` | GET | user | View request details |
| `/my/documents` | GET | user | List accessible documents |
| `/my/documents/<int:doc_id>/download` | GET | user | Download document (access_token) |
| `/my/payments` | GET | user | Payment history |
| `/my/inspections` | GET | user | Upcoming/past inspections |
| `/my/inspections/<int:id>/confirm` | POST | user | Confirm inspection access |

### 3.2 Access Control

**Record Rules (`security/ir.model.access.csv`):**
```python
# Tenant can only see their own tenancy
domain = [('tenant_ids', 'in', [user.partner_id.id])]

# Permitted occupier - read only
domain = [('permitted_occupier_ids', 'in', [user.partner_id.id])]
```

**Security Groups:**
| Group | Access |
|-------|--------|
| `group_tenant_user` | Full tenant access |
| `group_tenant_occupier` | Read-only access |
| `group_tenant_guarantor` | Financial view only |

### 3.3 Model Extensions

#### `res.partner` (Extension)
| Field | Type | Description |
|-------|------|-------------|
| `is_tenant` | Boolean | Is this a tenant contact? |
| `tenant_portal_access` | Boolean | Has portal access? |
| `portal_email_verified` | Boolean | Email verified? |
| `emergency_contact_name` | Char | Emergency contact |
| `emergency_contact_phone` | Char | Emergency phone |
| `preferred_contact_method` | Selection | email/sms/phone |
| `notification_preferences` | Text (JSON) | Notification settings |

---

## 4. Data Models

### 4.1 Maintenance Request (Portal Extension)

Extends `property_fielder.maintenance.request`:

| Field | Type | Description |
|-------|------|-------------|
| `portal_submitted` | Boolean | Submitted via portal? |
| `access_arrangements` | Text | **Key/contact info for access** |
| `preferred_date_1` | Date | **First preferred date** |
| `preferred_date_2` | Date | **Second preferred date** |
| `preferred_date_3` | Date | **Third preferred date** |
| `tenant_rating` | Selection | 1-5 star rating |
| `tenant_feedback` | Text | Tenant feedback |
| `tenant_photos` | Many2many → ir.attachment | Photos from tenant |

### 4.2 Inspection Response (Portal Extension)

Extends `property_fielder.job`:

| Field | Type | Description |
|-------|------|-------------|
| `tenant_response_status` | Selection | **pending/confirmed/rescheduled/refused** |
| `tenant_response_date` | Datetime | **When tenant responded** |
| `tenant_reschedule_reason` | Text | **Reason for reschedule request** |
| `tenant_preferred_date` | Date | **Tenant's preferred alternative date** |

### 4.2 Messaging via mail.thread

**Note:** Do NOT create a custom `portal.message` model. Use Odoo's native `mail.thread` for all messaging.

```python
class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # All messages are stored in mail.message via chatter
    # Tenants can post messages via portal
    # Property managers reply via standard Odoo chatter
```

**Benefits:**
- Standard Odoo messaging infrastructure
- Email integration out of the box
- Attachment handling via ir.attachment
- Read tracking via mail.notification
- No custom model maintenance

---

## 5. Portal Features

### 5.1 Dashboard (`/my/tenancy`)
- Property address and photo
- Tenancy status (Active/Periodic/Ending)
- Current rent amount and due date
- Outstanding balance (if arrears)
- Open maintenance count
- Next inspection date
- Compliance certificate status (Gas/EICR/EPC)
- Important notices/alerts

### 5.2 My Tenancy (`/my/tenancy/<id>`)
- Tenancy start/end dates
- Rent breakdown (amount, frequency, due day)
- Deposit details (amount, scheme, reference)
- Named tenants and occupiers
- Landlord/Agent contact details
- Tenancy agreement download
- How to Rent guide (version served)

### 5.3 Maintenance Reporting (`/my/maintenance`)

#### New Request Form:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `category` | Selection | Yes | From predefined list |
| `description` | Text | Yes | Min 20 chars |
| `location` | Char | Yes | Room/area |
| `urgency` | Selection | Yes | normal/urgent/emergency |
| `photos` | File[] | No | Max 5, 10MB each, HEIC converted client-side |
| `preferred_dates` | Date[] | No | Future dates only |
| `access_arrangements` | Text | No | Key/contact info |

#### HEIC Image Handling (Client-Side Conversion)

**iPhone photos are often HEIC format. Convert client-side to avoid server dependencies:**

```javascript
// static/src/js/heic_converter.js
import heic2any from 'heic2any';

async function convertHeicToJpeg(file) {
    if (file.type === 'image/heic' || file.name.toLowerCase().endsWith('.heic')) {
        const blob = await heic2any({
            blob: file,
            toType: 'image/jpeg',
            quality: 0.85
        });
        return new File([blob], file.name.replace(/\.heic$/i, '.jpg'), {
            type: 'image/jpeg'
        });
    }
    return file;
}

// Hook into file upload widget
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        const converted = await Promise.all(files.map(convertHeicToJpeg));
        // Replace files with converted versions
        const dt = new DataTransfer();
        converted.forEach(f => dt.items.add(f));
        e.target.files = dt.files;
    });
});
```

**Note:** Uses `heic2any` npm package (MIT license). Add to `package.json`:
```json
{
  "dependencies": {
    "heic2any": "^0.0.4"
  }
}
```

### 5.4 Generic Document Upload (`/my/documents/upload`)

```python
class TenantPortalController(http.Controller):

    @http.route('/my/documents/upload', type='http', auth='user',
                methods=['POST'], website=True, csrf=True)
    def upload_document(self, **post):
        """Generic document upload for tenants."""
        tenancy_id = post.get('tenancy_id')
        document_type = post.get('document_type')  # e.g., 'id_proof', 'income_proof'
        file = post.get('file')

        if not file or not tenancy_id:
            return request.redirect('/my/documents?error=missing_data')

        tenancy = request.env['property_fielder.tenancy'].browse(int(tenancy_id))
        # Access check
        if request.env.user.partner_id not in tenancy.tenant_ids:
            return request.redirect('/my/documents?error=access_denied')

        # Create attachment
        attachment = request.env['ir.attachment'].sudo().create({
            'name': file.filename,
            'datas': base64.b64encode(file.read()),
            'res_model': 'property_fielder.tenancy',
            'res_id': tenancy.id,
            'type': 'binary',
        })

        # Link to document model if applicable
        if document_type:
            request.env['property_fielder.document'].sudo().create({
                'tenancy_id': tenancy.id,
                'document_type': document_type,
                'attachment_id': attachment.id,
                'uploaded_by': request.env.user.partner_id.id,
            })

        return request.redirect('/my/documents?success=uploaded')
```

#### Categories (UK Section 11 aligned):
| Category | Section 11 | Awaab Trigger |
|----------|------------|---------------|
| Heating/Hot Water | ✅ | No |
| Plumbing/Leaks | ✅ | Potential |
| Electrical Issues | ✅ | No |
| Damp/Mould/Condensation | ✅ | **Yes** |
| Doors/Windows/Security | ✅ | No |
| Appliances | If included | No |
| Pest Control | No | No |
| External/Garden | Partial | No |

---

## 6. UK Regulatory Compliance

### 6.1 Section 21 Awareness
- Portal shows if mandatory documents have been served
- Visual indicator: "Your tenancy documents are up to date" / "Documents pending"

### 6.2 Awaab's Law Integration
- Damp/Mould reports trigger Awaab's Law workflow
- Tenant sees: "Your report has been logged as a Health & Safety priority"
- Countdown visible: "Response due within X days"

### 6.3 GDPR Compliance

- Cookie consent banner
- Privacy policy link
- Data portability (export my data)
- Right to erasure request form

### 6.4 Document Access (Statutory Requirements)

**Tenants must have access to these documents:**

| Document | Access | Reason |
|----------|--------|--------|
| Gas Safety Certificate | ✅ Full | Statutory requirement |
| EICR | ✅ Full | Statutory requirement |
| EPC | ✅ Full | Statutory requirement |
| How to Rent Guide | ✅ Full | Statutory requirement |
| Tenancy Agreement | ✅ Full | Contract |
| Deposit Certificate | ✅ Full | Statutory requirement |
| Inventory | ✅ Full | Dispute resolution |
| Landlord ID | ❌ Hidden | GDPR |

### 6.5 Section 48 Address for Service (Landlord & Tenant Act 1987)

**Tenants must be provided with an address in England/Wales for service of notices:**

```python
class TenantPortalController(http.Controller):

    @http.route('/my/tenancy/<int:tenancy_id>', type='http', auth='user', website=True)
    def tenancy_details(self, tenancy_id, **kw):
        tenancy = request.env['property_fielder.tenancy'].browse(tenancy_id)
        # ... access checks ...

        # Section 48 Address for Service
        # Display agent's address (NOT landlord's personal address)
        section_48_address = tenancy.property_id.managing_agent_id.contact_address or \
                            request.env.company.partner_id.contact_address

        return request.render('property_fielder_tenant_portal.tenancy_details', {
            'tenancy': tenancy,
            'section_48_address': section_48_address,
            'section_48_label': 'Address for Service of Notices (Section 48)',
        })
```

**Template Display:**
```xml
<div class="alert alert-info">
    <strong t-esc="section_48_label"/>
    <address t-esc="section_48_address"/>
    <small>All notices relating to this tenancy should be sent to this address.</small>
</div>
```

---

## 7. User Onboarding Flow

### 7.1 Invitation Trigger

```python
class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    def action_activate_tenancy(self):
        """When tenancy becomes active, invite tenants to portal."""
        super().action_activate_tenancy()
        for tenant in self.tenant_ids:
            if not tenant.user_ids:
                # Create portal user and send invitation
                self._invite_tenant_to_portal(tenant)

    def _invite_tenant_to_portal(self, partner):
        """Create portal user and send activation email."""
        user = self.env['res.users'].sudo().create({
            'name': partner.name,
            'login': partner.email,
            'partner_id': partner.id,
            'groups_id': [(6, 0, [
                self.env.ref('base.group_portal').id,
                self.env.ref('property_fielder_tenant_portal.group_tenant_user').id,
            ])],
        })
        # Send password reset email
        user.action_reset_password()

        # Log invitation
        self.message_post(
            body=f"Portal invitation sent to {partner.name} ({partner.email})",
            message_type='notification',
        )
```

### 7.2 Activation Email Template

```xml
<record id="mail_template_tenant_portal_invite" model="mail.template">
    <field name="name">Tenant Portal Invitation</field>
    <field name="model_id" ref="base.model_res_users"/>
    <field name="subject">Welcome to Your Tenant Portal - ${object.partner_id.name}</field>
    <field name="body_html"><![CDATA[
<p>Dear ${object.partner_id.name},</p>

<p>Your tenancy at <strong>${object.partner_id.tenancy_ids[0].property_id.name}</strong>
is now active.</p>

<p>You can access your Tenant Portal to:</p>
<ul>
    <li>View your tenancy documents</li>
    <li>Report maintenance issues</li>
    <li>Check your payment history</li>
    <li>Download compliance certificates</li>
</ul>

<p><a href="${object.signup_url}">Click here to activate your account</a></p>

<p>This link expires in 7 days.</p>
    ]]></field>
</record>
```

---

## 8. Profile Management

### 8.1 Portal Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/my/profile` | GET | View profile |
| `/my/profile/edit` | GET/POST | Edit contact details |
| `/my/profile/password` | GET/POST | Change password |
| `/my/profile/notifications` | GET/POST | Notification preferences |

### 8.2 Editable Fields

| Field | Editable | Notes |
|-------|----------|-------|
| Email | ✅ | Requires verification |
| Phone | ✅ | |
| Emergency Contact | ✅ | |
| Preferred Contact Method | ✅ | |
| Notification Preferences | ✅ | |
| Name | ❌ | Requires admin |
| Address | ❌ | Linked to tenancy |

---

## 9. Notice to Vacate

### 9.1 Portal Route

| Route | Method | Description |
|-------|--------|-------------|
| `/my/tenancy/<id>/notice` | GET | View notice form |
| `/my/tenancy/<id>/notice` | POST | Submit notice to vacate |

### 9.2 Notice Submission Form

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `intended_vacate_date` | Date | Yes | Min notice period from tenancy |
| `reason` | Selection | No | moving/buying/other |
| `forwarding_address` | Text | No | For deposit return |
| `confirmation` | Checkbox | Yes | "I understand this is binding" |

### 9.3 Notice Workflow

```python
class TenancyPortal(portal.CustomerPortal):

    @http.route('/my/tenancy/<int:tenancy_id>/notice', type='http',
                auth='user', methods=['POST'])
    def submit_notice(self, tenancy_id, **post):
        """Tenant submits notice to vacate."""
        tenancy = request.env['property_fielder.tenancy'].sudo().browse(tenancy_id)

        # Security check
        if request.env.user.partner_id not in tenancy.tenant_ids:
            return request.redirect('/my?error=access_denied')

        # Validate notice period
        vacate_date = fields.Date.from_string(post.get('intended_vacate_date'))
        min_notice = tenancy.notice_period_days or 30
        earliest_date = fields.Date.today() + timedelta(days=min_notice)

        if vacate_date < earliest_date:
            return request.redirect(
                f'/my/tenancy/{tenancy_id}/notice?error=insufficient_notice'
            )

        # Create notice record
        tenancy.write({
            'notice_served_by': 'tenant',
            'notice_served_date': fields.Date.today(),
            'intended_vacate_date': vacate_date,
            'forwarding_address': post.get('forwarding_address'),
        })

        # Notify property manager
        template = request.env.ref('property_fielder_tenant_portal.email_notice_received')
        template.sudo().send_mail(tenancy.id)

        return request.redirect(f'/my/tenancy/{tenancy_id}?message=notice_submitted')
```

---

## 10. Payment History

### 10.1 Payment View (Read-Only)

**Note:** This portal provides **read-only** payment history. Online payment functionality requires the `payment` module and payment acquirer integration (Stripe/GoCardless).

| Data Shown | Source |
|------------|--------|
| Invoice Date | `account.move.invoice_date` |
| Due Date | `account.move.invoice_date_due` |
| Amount | `account.move.amount_total` |
| Status | `account.move.payment_state` |
| Payment Date | `account.payment.date` |

### 10.2 Outstanding Balance Calculation

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    tenant_outstanding_balance = fields.Monetary(
        compute='_compute_tenant_balance',
        string='Outstanding Balance'
    )

    @api.depends('invoice_ids.amount_residual')
    def _compute_tenant_balance(self):
        for partner in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
            ])
            partner.tenant_outstanding_balance = sum(invoices.mapped('amount_residual'))
```

---

## 11. Mobile Responsiveness

### 11.1 Mobile-First Design

```python
# Portal templates use Bootstrap 5 responsive grid
# All forms optimized for mobile input
# Photo upload uses device camera API
# Touch-friendly buttons (min 44px tap target)
```

### 11.2 PWA Support (Future)

- Offline maintenance request drafts
- Push notifications for updates
- Add to home screen

### 11.3 HEIC Photo Handling

```python
def _process_uploaded_photo(self, file):
    """Convert HEIC to JPEG for compatibility."""
    if file.filename.lower().endswith('.heic'):
        # Use pillow-heif for conversion
        from pillow_heif import register_heif_opener
        register_heif_opener()
        img = Image.open(file)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    return file.read()
```

---

## 12. Guarantor Access Rules

### 12.1 Strict Record Rules

```python
# Guarantor can ONLY see financial data
('guarantor_tenancy_rule', 'property_fielder.tenancy',
 "[('guarantor_id', '=', user.partner_id.id)]", 'group_tenant_guarantor')

# Guarantor CANNOT see maintenance requests
('guarantor_maintenance_deny', 'property_fielder.maintenance.request',
 "[(0, '=', 1)]", 'group_tenant_guarantor')  # Always false = no access

# Guarantor CANNOT see messages
('guarantor_message_deny', 'mail.message',
 "[(0, '=', 1)]", 'group_tenant_guarantor')
```

### 12.2 Guarantor Portal View

| Data Visible | Data Hidden |
|--------------|-------------|
| Tenancy dates | Maintenance requests |
| Rent amount | Messages/chatter |
| Payment history | Tenant photos |
| Outstanding balance | Inspection details |
| Tenancy agreement | Personal documents |

---

## 13. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models defined | ✅ Complete |
| **account dependency added** | ✅ Added |
| **access_arrangements field** | ✅ Added |
| **preferred_dates fields** | ✅ Added |
| **tenant_response_status field** | ✅ Added |
| **User onboarding flow** | ✅ Added |
| **Invitation email template** | ✅ Added |
| **Profile management routes** | ✅ Added |
| **Notice to vacate feature** | ✅ Added |
| **Payment history (read-only clarified)** | ✅ Added |
| **Outstanding balance calculation** | ✅ Added |
| **Guarantor access rules** | ✅ Added |
| **HEIC photo handling (client-side JS)** | ✅ Added |
| **Generic document upload route** | ✅ Added |
| **Section 48 Address for Service** | ✅ Added |
| **Document access matrix** | ✅ Added |
| **Mobile responsiveness** | ✅ Added |
| **PWA support (future)** | ✅ Added |
| **Uses mail.thread for messaging** | ✅ Fixed |
| Portal routes specified | ✅ Complete |
| Access control defined | ✅ Complete |
| UK regulatory compliance | ✅ Complete |
| **Overall** | ✅ Ready for Review |

