# PRD: Property Fielder Defects

**Addon Name:** `property_fielder_defects`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Domain (Layer 3)  
**Phase:** Phase 3 (Defects & Remediation)  
**Effort:** 26 days  

---

## 1. Overview

Unified defect/fault tracking with native industry codes and SLA management.

### 1.1 Purpose
Track all property defects from discovery through remediation with proper fault coding, contractor assignment, and SLA enforcement.

### 1.2 Target Users
- Compliance Managers
- Dispatch Managers
- Contractors
- Landlords (cost approval)

### 1.3 Business Value
- Unified defect tracking (no separate systems)
- Native industry fault codes
- Automatic deadline calculation
- Contractor management
- Cost approval workflow

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for audit trail
    'account',  # Invoice/bill creation
    'purchase',  # Contractor POs
    'property_fielder_property_management',
    'property_fielder_templates',  # For inspection.response extension
]

# Note: This addon EXTENDS inspection.response to add defect_id
# This avoids circular dependency (templates doesn't know about defects)
```

---

## 3. Data Models

### 3.1 `property_fielder.fault.code`
Reference data for industry fault codes.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Code name |
| `code` | Char | Industry code |
| `category` | Selection | gas/electrical/fire/legionella/asbestos |
| `standard` | Char | e.g., "GIUSP", "18th Edition", "RRO 2005" |
| `description` | Text | Code description |
| `severity_sla` | Char | Default severity (C1, C2, AR, ID, NCS) |
| `deadline_days` | Integer | SLA deadline in days |
| `is_immediate` | Boolean | Requires immediate action |
| `active` | Boolean | Code is active |

### 3.2 `property_fielder.defect`
Unified defect record.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Defect reference (auto-sequence) |
| `property_id` | Many2one → property | Property |
| `inspection_id` | Many2one → inspection | Source inspection |
| `response_id` | Many2one → response | Template response that created it |
| `defect_type` | Selection | regulatory_fault/hhsrs_hazard |
| `fault_code_id` | Many2one → fault.code | Industry fault code |
| `description` | Text | Defect description |
| `location` | Char | Location within property |
| `severity_sla` | Char | Severity (C1/C2/C3/NCS/AR/ID) |
| `reported_date` | Date | When reported |
| `deadline_date` | Date | Computed SLA deadline |
| `state` | Selection | reported/acknowledged/in_progress/fixed/verified/closed |
| `assigned_contractor_id` | Many2one → contractor | Assigned contractor |
| `estimated_cost` | Float | Estimated repair cost |
| `actual_cost` | Float | Actual repair cost |
| `cost_approved` | Boolean | Landlord approved cost |
| `cost_approval_id` | Many2one → cost.approval | Approval record |
| `remediation_ids` | One2many → remediation | Remediation work records |
| `photo_ids` | Many2many → job.photo | Evidence photos |
| `priority` | Selection | low/medium/high/urgent/emergency |
| `landlord_refused` | Boolean | Landlord refused repair |
| `refusal_date` | Date | When refused |
| `tenancy_warning_sent` | Boolean | Termination warning sent |
| `tenant_liability` | Boolean | **Tenant caused damage** |
| `tenant_recharge` | Boolean | **Recharge to tenant** |
| `invoice_id` | Many2one → account.move | **Finance: Invoice for costs** |
| `purchase_order_id` | Many2one → purchase.order | **Contractor PO** |
| `asset_response_id` | Many2one → asset.response | **Asset response (for CP12/EICR)** |

### 3.3 Inspection Response Extension

**This addon extends `property_fielder.inspection.response` to add defect linkage:**

```python
class InspectionResponse(models.Model):
    _inherit = 'property_fielder.inspection.response'

    defect_id = fields.Many2one(
        'property_fielder.defect',
        string='Created Defect',
        help="Defect created from this response"
    )

    def action_create_defect(self):
        """Create defect from failed inspection response."""
        if not self.creates_defect:
            return
        defect = self.env['property_fielder.defect'].create({
            'property_id': self.inspection_id.property_id.id,
            'inspection_id': self.inspection_id.id,
            'response_id': self.id,
            'fault_code_id': self.item_id.fault_code_id.id,
            'severity_sla': self.item_id.defect_severity,
            'description': f"{self.item_id.question}: {self.response_text}",
        })
        self.defect_id = defect.id
        return defect
```

### 3.4 `property_fielder.contractor`
Contractor management.

| Field | Type | Description |
|-------|------|-------------|
| `partner_id` | Many2one → res.partner | Contact record |
| `name` | Char | Company name |
| `trade_ids` | Many2many → contractor.trade | Trades (Gas, Electrical, etc.) |
| `accreditation_ids` | One2many → contractor.accreditation | Accreditations |
| `rating` | Float | Average rating (1-5) |
| `preferred` | Boolean | Preferred contractor |
| `hourly_rate` | Float | Hourly rate |
| `active` | Boolean | Available for work |
| `cis_registered` | Boolean | CIS registered |
| `cis_deduction_rate` | Float | CIS deduction % |

### 3.4 `property_fielder.contractor.accreditation`
Contractor certifications.

| Field | Type | Description |
|-------|------|-------------|
| `contractor_id` | Many2one → contractor | Contractor |
| `accreditation_type` | Selection | gas_safe/niceic/napit/etc |
| `registration_number` | Char | Registration number |
| `expiry_date` | Date | Expiry date |
| `verified` | Boolean | Verified with authority |
| `verified_date` | Date | Last verification date |
| `document` | Binary | Certificate scan |

### 3.5 `property_fielder.defect.remediation`
Remediation work record.

| Field | Type | Description |
|-------|------|-------------|
| `defect_id` | Many2one → defect | Parent defect |
| `contractor_id` | Many2one → contractor | Contractor |
| `job_id` | Many2one → job | Field service job |
| `scheduled_date` | Date | Scheduled date |
| `completed_date` | Date | Completion date |
| `work_description` | Text | Work performed |
| `parts_used` | Text | Parts/materials |
| `labor_hours` | Float | Labor hours |
| `labor_cost` | Float | Labor cost |
| `parts_cost` | Float | Parts cost |
| `total_cost` | Float | Total cost |
| `state` | Selection | scheduled/in_progress/completed/verified |
| `verified_by` | Many2one → res.users | Who verified |
| `verified_date` | Datetime | Verification date |

### 3.6 `property_fielder.cost.approval`
Landlord cost approval workflow.

| Field | Type | Description |
|-------|------|-------------|
| `defect_id` | Many2one → defect | Defect |
| `landlord_id` | Many2one → res.partner | Landlord |
| `estimated_cost` | Float | Cost to approve |
| `state` | Selection | pending/approved/rejected |
| `requested_date` | Datetime | When requested |
| `responded_date` | Datetime | When responded |
| `notes` | Text | Landlord notes |

### 3.7 `property_fielder.access.attempt`

**Log of attempts to access property for defect remediation.**

| Field | Type | Description |
|-------|------|-------------|
| `defect_id` | Many2one → defect | Parent defect |
| `property_id` | Many2one → property | Property (related) |
| `attempt_date` | Datetime | When access was attempted |
| `result` | Selection | **granted/refused/no_answer/rescheduled** |
| `reason` | Text | Reason for refusal/reschedule |
| `contractor_id` | Many2one → contractor | Contractor who attempted |
| `notes` | Text | Additional notes |
| `photo_ids` | Many2many → ir.attachment | Evidence photos (e.g., door photo) |

**UK Legal Context:**
- Under Section 11 Landlord & Tenant Act 1985, landlord must give 24h notice
- Tenant cannot unreasonably refuse access
- 3+ refusals may constitute breach of tenancy
- Evidence of access attempts is critical for possession proceedings

### 3.8 `property_fielder.improvement.notice`

**Local Authority Improvement Notice tracking (Housing Act 2004).**

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `defect_ids` | Many2many → defect | Related defects |
| `notice_type` | Selection | **improvement/prohibition/emergency_prohibition** |
| `served_date` | Date | Date notice served |
| `compliance_deadline` | Date | Deadline for compliance |
| `local_authority` | Char | Issuing authority name |
| `reference_number` | Char | LA reference number |
| `document_id` | Many2one → ir.attachment | Scanned notice |
| `state` | Selection | **active/complied/appealed/withdrawn** |
| `compliance_date` | Date | Date compliance achieved |
| `appeal_date` | Date | Date of appeal (if any) |

**UK Legal Context:**
- Improvement Notice: 28 days minimum to comply
- Prohibition Notice: Restricts use of property
- Emergency Prohibition: Immediate effect
- Failure to comply is criminal offense (unlimited fine)

---

## 4. Key Features

### 4.1 Native Fault Codes
- GIUSP (Gas Industry Unsafe Situations Procedure)
- 18th Edition (Electrical)
- RRO 2005 (Fire Safety)
- HSE L8 (Legionella)
- CAR 2012 (Asbestos)

### 4.2 Gas Severity Codes (GIUSP)

| Code | Full Name | Description | Deadline | Action |
|------|-----------|-------------|----------|--------|
| **ID** | Immediately Dangerous | Danger to life | **Immediate** | Disconnect, cap off |
| **AR** | At Risk | Danger if circumstances change | **24 hours** | Repair or disconnect |
| **NCS** | Not to Current Standard | Non-compliant but safe | **Advised** | Recommend upgrade |

### 4.3 Electrical Severity Codes (BS 7671 18th Edition)

| Code | Full Name | Description | Deadline | Action |
|------|-----------|-------------|----------|--------|
| **C1** | Danger Present | Immediate risk of injury | **Immediate** | Isolate, repair |
| **C2** | Potentially Dangerous | Risk of injury under certain conditions | **28 days** | Schedule repair |
| **C3** | Improvement Recommended | Not compliant but not dangerous | **Advised** | Recommend improvement |
| **FI** | Further Investigation | Cannot determine; requires investigation | **28 days** | Schedule investigation |

### 4.4 Fire Safety Codes (RRO 2005)

| Priority | Description | Deadline |
|----------|-------------|----------|
| **P1** | Life-threatening | 24 hours |
| **P2** | High risk | 7 days |
| **P3** | Medium risk | 28 days |
| **P4** | Low risk | Routine |

### 4.5 Unified Severity → Deadline Mapping

```python
SEVERITY_DEADLINES = {
    # Gas (GIUSP)
    'ID': timedelta(hours=0),   # Immediate
    'AR': timedelta(hours=24),
    'NCS': None,  # Advisory
    # Electrical (BS 7671)
    'C1': timedelta(hours=0),   # Immediate
    'C2': timedelta(days=28),
    'C3': None,  # Advisory
    'FI': timedelta(days=28),
    # Fire (RRO 2005)
    'P1': timedelta(hours=24),
    'P2': timedelta(days=7),
    'P3': timedelta(days=28),
    'P4': None,  # Routine
    # HHSRS
    'band_a': timedelta(hours=24),  # Category 1
    'band_b': timedelta(days=28),
    'band_c': timedelta(days=90),
}
```

### 4.3 Contractor Assignment
- Match by trade and accreditation
- Check accreditation validity
- Track contractor ratings
- CIS deduction support

### 4.4 Cost Approval Workflow
- Auto-request for costs over threshold
- Email notification to landlord
- Approval portal for landlords
- Track refusals with termination warning

### 4.5 Re-Check Scheduling
- Schedule verification visit after fix
- Invoice blocking on failed re-check
- Automatic defect state updates

### 4.6 Guest Upload Link (Magic Link)

**Secure token-based access for external contractors:**

```python
class Defect(models.Model):
    _inherit = 'property_fielder.defect'

    access_token = fields.Char(
        string='Access Token',
        copy=False,
        help="Secure token for guest upload link"
    )
    access_url = fields.Char(
        compute='_compute_access_url',
        string='Guest Upload URL'
    )
    access_token_expiry = fields.Datetime(
        string='Token Expiry',
        help="Token expires after this date"
    )

    def _compute_access_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if rec.access_token:
                rec.access_url = f"{base_url}/defect/upload/{rec.id}/{rec.access_token}"
            else:
                rec.access_url = False

    def action_generate_access_token(self):
        """Generate secure access token for guest upload."""
        import secrets
        for rec in self:
            rec.access_token = secrets.token_urlsafe(32)
            rec.access_token_expiry = fields.Datetime.now() + timedelta(days=7)
        return True

    def action_revoke_access_token(self):
        """Revoke access token."""
        self.write({'access_token': False, 'access_token_expiry': False})
```

**Guest Upload Controller:**

```python
class DefectGuestController(http.Controller):

    @http.route('/defect/upload/<int:defect_id>/<string:token>',
                type='http', auth='public', website=True)
    def guest_upload_page(self, defect_id, token, **kwargs):
        defect = request.env['property_fielder.defect'].sudo().browse(defect_id)
        if not defect.exists() or defect.access_token != token:
            return request.not_found()
        if defect.access_token_expiry < fields.Datetime.now():
            return request.render('property_fielder_defects.token_expired')
        return request.render('property_fielder_defects.guest_upload', {
            'defect': defect,
        })

    @http.route('/defect/upload/<int:defect_id>/<string:token>/submit',
                type='http', auth='public', methods=['POST'], csrf=False)
    def guest_upload_submit(self, defect_id, token, **kwargs):
        # Validate token, save uploaded files to defect.photo_ids
        pass
```

### 4.7 Section 20 Consultation (Landlord & Tenant Act 1985)

**For leasehold properties, works over £250 require Section 20 consultation:**

```python
class Defect(models.Model):
    _inherit = 'property_fielder.defect'

    section_20_required = fields.Boolean(
        compute='_compute_section_20_required',
        store=True,
        help="Section 20 consultation required for works over £250"
    )
    section_20_consultation_id = fields.Many2one(
        'property_fielder.section20.consultation',
        string='Section 20 Consultation'
    )

    @api.depends('estimated_cost', 'property_id.tenure_type')
    def _compute_section_20_required(self):
        """
        Section 20 Landlord & Tenant Act 1985:
        - Applies to leasehold properties only
        - Required when works cost > £250 per leaseholder
        - Consultation process takes minimum 30 days
        """
        for rec in self:
            rec.section_20_required = (
                rec.property_id.tenure_type == 'leasehold' and
                rec.estimated_cost > 250.00
            )

class Section20Consultation(models.Model):
    _name = 'property_fielder.section20.consultation'
    _description = 'Section 20 Consultation Process'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    defect_ids = fields.Many2many('property_fielder.defect')
    property_id = fields.Many2one('property_fielder.property')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('notice_of_intention', 'Notice of Intention Sent'),  # Stage 1
        ('observation_period', 'Observation Period'),  # 30 days
        ('statement_of_estimates', 'Statement of Estimates'),  # Stage 2
        ('second_observation', 'Second Observation Period'),  # 30 days
        ('works_approved', 'Works Approved'),
        ('dispensation_applied', 'Dispensation Applied'),
    ])
    notice_of_intention_date = fields.Date()
    observation_deadline = fields.Date()
    leaseholder_observations = fields.Text()
    estimates_sent_date = fields.Date()
    final_deadline = fields.Date()
```

**UK Legal Context:**
- **Stage 1:** Notice of Intention - describe works, invite observations (30 days)
- **Stage 2:** Statement of Estimates - at least 2 quotes, invite observations (30 days)
- **Dispensation:** Can apply to First-tier Tribunal to skip consultation (emergency works)
- **Penalty:** Without consultation, landlord can only recover £250 per leaseholder

---

## 5. Integration with Odoo Finance

### 5.1 Account Move (Invoice) Link

```python
class Defect(models.Model):
    _inherit = 'property_fielder.defect'

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        domain=[('move_type', 'in', ['out_invoice', 'in_invoice'])]
    )

    def action_create_invoice(self):
        """Create supplier invoice for contractor costs."""
        return self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.assigned_contractor_id.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Defect repair: {self.name}',
                'quantity': 1,
                'price_unit': self.actual_cost,
            })]
        })
```

### 5.2 Tenant Recharge

- If `tenant_liability = True`, create out_invoice to tenant
- Link to tenancy deposit deduction if applicable
- Track disputed recharges

---

## 6. Section 21 Blocking Logic

### 6.1 Compliance Check for Eviction

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    section_21_blocked = fields.Boolean(
        compute='_compute_section_21_blocked',
        store=True,
        help="True if Section 21 notice cannot be served due to open defects"
    )
    section_21_block_reasons = fields.Text(
        compute='_compute_section_21_blocked',
        store=True
    )

    @api.depends('defect_ids.state', 'defect_ids.severity_sla')
    def _compute_section_21_blocked(self):
        """
        Section 21 Housing Act 1988 cannot be served if:
        1. Outstanding Category 1 HHSRS hazards (Band A/B)
        2. Outstanding ID/AR gas defects
        3. Outstanding C1/C2 electrical defects
        4. Improvement Notice served by Local Authority
        """
        blocking_severities = ['ID', 'AR', 'C1', 'C2', 'band_a', 'band_b']
        for prop in self:
            open_defects = prop.defect_ids.filtered(
                lambda d: d.state not in ['fixed', 'verified', 'closed']
                and d.severity_sla in blocking_severities
            )
            prop.section_21_blocked = bool(open_defects)
            if open_defects:
                prop.section_21_block_reasons = '\n'.join([
                    f"- {d.name}: {d.severity_sla} - {d.description[:50]}"
                    for d in open_defects
                ])
            else:
                prop.section_21_block_reasons = False
```

### 6.2 Access Attempt Logging

```python
class Defect(models.Model):
    _inherit = 'property_fielder.defect'

    access_attempt_ids = fields.One2many(
        'property_fielder.access.attempt',
        'defect_id',
        string='Access Attempts',
        help="Log of attempts to access property for this defect"
    )
    access_refused_count = fields.Integer(
        compute='_compute_access_refused',
        store=True
    )

    @api.depends('access_attempt_ids.result')
    def _compute_access_refused(self):
        for rec in self:
            rec.access_refused_count = len(rec.access_attempt_ids.filtered(
                lambda a: a.result == 'refused'
            ))
```

---

## 7. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **defect_id added via inheritance** | ✅ Added |
| **asset_response_id for CP12/EICR** | ✅ Added |
| **templates dependency added** | ✅ Fixed |
| **mail/account/purchase dependencies** | ✅ Added |
| **Section 21 blocking logic** | ✅ Added |
| **Access attempt logging** | ✅ Added |
| **access.attempt model defined** | ✅ Added |
| **access_token for Magic Link** | ✅ Added |
| **access_url computed field** | ✅ Added |
| **Guest upload controller** | ✅ Added |
| **Section 20 consultation check** | ✅ Added |
| **Improvement Notice model** | ✅ Added |
| Split Gas/Electrical codes | ✅ Complete |
| Tenant liability boolean | ✅ Complete |
| Finance link to account.move | ✅ Complete |
| Fault codes defined | ✅ Complete |
| SLA mapping specified | ✅ Complete |
| Contractor workflow clear | ✅ Complete |
| **Overall** | ✅ Ready for Review |

