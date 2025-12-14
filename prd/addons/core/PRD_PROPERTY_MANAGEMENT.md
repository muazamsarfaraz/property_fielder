# PRD: Property Fielder Property Management

**Addon Name:** `property_fielder_property_management`
**Version:** 2.0.0
**Status:** ✅ Built
**Layer:** Core (Layer 1)

---

## 1. Overview

Property portfolio management with UK FLAGE+ certification compliance tracking.

### 1.1 Purpose

Manage property portfolios with comprehensive tracking of UK regulatory certifications (Fire, Legionella, Asbestos, Gas, Electrical, EPC, PAT).

### 1.2 Target Users

- Compliance Managers
- Property Managers
- Landlords

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',
    'web',
    'property_fielder_field_service',
]
```

**Note:** This module depends on Field Service for job creation. Tenancy management is in a separate `property_fielder_property_leasing` addon.

---

## 3. Data Models

### 3.1 `property_fielder.property`

Core property/asset model. Inherits `mail.thread` for chatter.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Property name/reference |
| `uprn` | Char | **Unique Property Reference Number (UK)** |
| `address` | Text | Full address |
| `address_line_1` | Char | Address line 1 |
| `address_line_2` | Char | Address line 2 |
| `city` | Char | City/Town |
| `county` | Char | County |
| `postcode` | Char | UK postcode |
| `country_id` | Many2one → res.country | Country |
| `latitude` | Float | GPS latitude |
| `longitude` | Float | GPS longitude |
| `property_type` | Selection | house/flat/hmo/commercial/block |
| `parent_id` | Many2one → self | Parent block (for units) |
| `child_ids` | One2many → self | Child units |
| `owner_id` | Many2one → res.partner | Property owner/landlord |
| `managing_agent_id` | Many2one → res.partner | Managing agent (if different) |
| `state` | Selection | prospect/onboarding/active/void/offboarding/archive |
| `bedrooms` | Integer | Number of bedrooms |
| `bathrooms` | Integer | Number of bathrooms |
| `reception_rooms` | Integer | Number of reception rooms |
| `floor_area_sqm` | Float | Floor area (sq meters) |
| `build_year` | Integer | Year built |
| `tenure` | Selection | freehold/leasehold/rental |
| `council_tax_band` | Selection | **A/B/C/D/E/F/G/H** |
| `furnishing_state` | Selection | **unfurnished/part_furnished/furnished** |
| `hmo_status` | Selection | **exempt/licensed/pending/unlicensed** |
| `hmo_license_number` | Char | License number |
| `hmo_license_expiry` | Date | License expiry date |
| `hmo_max_occupancy` | Integer | **Maximum permitted occupants** |
| `selective_license_required` | Boolean | **Selective licensing area** |
| `selective_license_number` | Char | Selective license number |
| `selective_license_expiry` | Date | Selective license expiry |
| `section_21_banned` | Boolean | Section 21 eviction banned |
| `epc_rating` | Selection | A/B/C/D/E/F/G |
| `epc_score` | Integer | EPC score (1-100) |
| `epc_exempt` | Boolean | EPC exemption registered |
| `epc_exempt_reason` | Selection | listed_building/cost_cap/etc |
| `certification_ids` | One2many → property_fielder.certification | Certifications |
| `inspection_ids` | One2many → property_fielder.inspection | Inspections |
| `job_ids` | One2many → property_fielder.job | **Jobs at this property** |
| `key_set_ids` | One2many → property_fielder.key.set | **Key sets for property** |
| `image_ids` | Many2many → ir.attachment | **Property photos** |
| `notes` | Text | Internal notes |

### 3.2 `property_fielder.certification.type`
Certification types (FLAGE+ categories).

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Type name (e.g., "Gas Safety") |
| `code` | Char | Code (F/L/A/G/E/EPC/PAT) |
| `category` | Selection | fire/legionella/asbestos/gas/electrical/epc/pat |
| `validity_months` | Integer | Certificate validity period |
| `warning_days` | Integer | Days before expiry to warn |
| `is_mandatory` | Boolean | Legally required |
| `inspection_template_id` | Many2one → inspection.template | Default template |
| `required_skills` | Many2many → property_fielder.skill | Required inspector skills |

### 3.3 `property_fielder.certification`
Individual certificate records.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property_fielder.property | Property |
| `certification_type_id` | Many2one → certification.type | Type |
| `certificate_number` | Char | Certificate reference |
| `issue_date` | Date | When issued |
| `expiry_date` | Date | When expires |
| `state` | Selection | valid/expiring_soon/expired/not_required |
| `inspector_id` | Many2one → res.partner | Issuing inspector |
| `attachment_id` | Many2one → ir.attachment | **Certificate PDF (proper Odoo pattern)** |
| `inspection_id` | Many2one → property_fielder.inspection | Linked inspection |
| `notes` | Text | Notes |

### 3.4 `property_fielder.inspection`

Inspection records.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property_fielder.property | Property |
| `certification_type_id` | Many2one → certification.type | Certification type |
| `job_id` | Many2one → property_fielder.job | Field service job |
| `inspector_id` | Many2one → res.partner | Inspector |
| `scheduled_date` | Date | Scheduled date |
| `completed_date` | Date | Completion date |
| `state` | Selection | scheduled/in_progress/completed/cancelled |
| `result` | Selection | pass/fail/remediation_required |
| `notes` | Text | Inspection notes |
| `next_due_date` | Date | Next inspection due |

### 3.5 `property_fielder.key.set`

Key set tracking for property access.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `name` | Char | Key set name (e.g., "Main Set 1") |
| `barcode` | Char | **Barcode/QR for scanning** |
| `key_type` | Selection | main/spare/contractor/emergency |
| `location` | Selection | **office/safe/contractor/tenant** |
| `branch_id` | Many2one → res.company | **Branch/office holding keys** |
| `quantity` | Integer | Number of keys in set |
| `state` | Selection | available/checked_out/lost/returned |
| `current_holder_id` | Many2one → res.partner | Current holder |
| `notes` | Text | Notes |

### 3.6 `property_fielder.access.code`

Access codes for property entry (alarm, gate, keypad).

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `code_type` | Selection | alarm/gate/keypad/lockbox/other |
| `code_value` | Char | **The code (encrypted storage recommended)** |
| `location` | Char | Where the code is used |
| `notes` | Text | Additional instructions |
| `last_changed` | Date | When code was last changed |
| `active` | Boolean | Is code still valid? |

### 3.7 `property_fielder.utility.meter`

Utility meter tracking for void management.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `meter_type` | Selection | gas/electricity/water |
| `serial_number` | Char | **Meter serial number** |
| `mpan_mprn` | Char | **MPAN (elec) or MPRN (gas)** |
| `supplier_id` | Many2one → res.partner | Current supplier |
| `location` | Char | Meter location |
| `is_smart_meter` | Boolean | Smart meter installed? |
| `reading_ids` | One2many → meter.reading | Meter readings |

### 3.8 `property_fielder.meter.reading`

Meter reading records.

| Field | Type | Description |
|-------|------|-------------|
| `meter_id` | Many2one → utility.meter | Meter |
| `reading_date` | Date | Date of reading |
| `reading_value` | Float | Meter reading |
| `reading_type` | Selection | actual/estimated/opening/closing |
| `photo_id` | Many2one → ir.attachment | Photo evidence |
| `recorded_by` | Many2one → res.users | Who recorded |

### 3.9 `property_fielder.building.insurance`

Buildings insurance tracking.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `provider_id` | Many2one → res.partner | Insurance provider |
| `policy_number` | Char | Policy number |
| `start_date` | Date | Policy start |
| `expiry_date` | Date | Policy expiry |
| `sum_insured` | Monetary | Sum insured |
| `currency_id` | Many2one → res.currency | Currency |
| `premium_annual` | Monetary | Annual premium |
| `excess_amount` | Monetary | Excess amount |
| `covers_flood` | Boolean | Flood cover included? |
| `covers_subsidence` | Boolean | Subsidence cover? |
| `attachment_id` | Many2one → ir.attachment | Policy document |
| `state` | Selection | active/expiring/expired |

### 3.10 `property_fielder.ews1.assessment`

EWS1 Fire Safety Assessment for blocks (Fire Safety Act 2021).

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Block property |
| `assessment_date` | Date | Assessment date |
| `assessor_id` | Many2one → res.partner | Assessor |
| `ews1_rating` | Selection | **A1/A2/A3/B1/B2** |
| `cladding_type` | Selection | none/acm/hpl/other |
| `height_meters` | Float | Building height |
| `remediation_required` | Boolean | Remediation needed? |
| `remediation_cost` | Monetary | Estimated cost |
| `remediation_fund_applied` | Boolean | Building Safety Fund applied? |
| `attachment_id` | Many2one → ir.attachment | EWS1 form |
| `notes` | Text | Notes |

### 3.11 `property_fielder.hmo.room`

Individual room tracking for HMO licensing (overcrowding compliance).

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | HMO property |
| `name` | Char | Room name/number (e.g., "Room 1", "Bedroom A") |
| `room_type` | Selection | bedroom/kitchen/bathroom/living/utility |
| `floor_area_sqm` | Float | **Room floor area (sq meters)** |
| `ceiling_height_m` | Float | **Ceiling height (meters)** |
| `max_occupants` | Integer | **Maximum occupants for this room** |
| `has_window` | Boolean | Has openable window? |
| `has_heating` | Boolean | Has adequate heating? |
| `has_fire_door` | Boolean | Fire door fitted? |
| `current_tenant_id` | Many2one → res.partner | Current occupant |
| `notes` | Text | Notes |

**HMO Room Size Standards (UK):**
- Single bedroom: minimum 6.51 sqm
- Double bedroom: minimum 10.22 sqm
- Shared room (2 persons): minimum 10.22 sqm
- Kitchen (1-5 persons): minimum 7 sqm

```python
@api.constrains('floor_area_sqm', 'room_type', 'max_occupants')
def _check_room_size_standards(self):
    """Validate room meets HMO minimum size standards."""
    for rec in self:
        if rec.room_type == 'bedroom':
            if rec.max_occupants == 1 and rec.floor_area_sqm < 6.51:
                raise ValidationError(
                    f"Single bedroom must be at least 6.51 sqm. "
                    f"Room '{rec.name}' is only {rec.floor_area_sqm} sqm."
                )
            elif rec.max_occupants >= 2 and rec.floor_area_sqm < 10.22:
                raise ValidationError(
                    f"Double/shared bedroom must be at least 10.22 sqm. "
                    f"Room '{rec.name}' is only {rec.floor_area_sqm} sqm."
                )
```

### 3.12 Additional Property Fields

Add to `property_fielder.property`:

| Field | Type | Description |
|-------|------|-------------|
| `council_tax_account` | Char | **Council Tax account number** |
| `room_ids` | One2many → hmo.room | **HMO rooms (for licensed HMOs)** |
| `income_account_id` | Many2one → account.account | **Default rent income account** |

---

## 4. Key Features

### 4.1 FLAGE+ Compliance
- Fire Safety Certificate tracking
- Legionella Risk Assessment tracking
- Asbestos Survey tracking
- Gas Safety Certificate (CP12) tracking
- Electrical Installation Condition Report (EICR) tracking
- EPC rating and exemption tracking
- PAT testing tracking

### 4.2 Property Lifecycle
- Prospect → Onboarding → Active → Void → Offboarding → Archive
- Automated state transitions
- Compliance requirements per state

### 4.3 Block/Unit Hierarchy
- Parent block with child units
- Cascading compliance (unit inherits block status)
- Fire Safety Act compliance for blocks

**EWS1 Cascade Logic (Block → Units):**

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    ews1_status = fields.Selection(
        [('pending', 'Pending'), ('pass', 'Pass'), ('fail', 'Fail'), ('na', 'N/A')],
        compute='_compute_ews1_status', store=True
    )

    @api.depends('parent_id.ews1_assessment_ids', 'ews1_assessment_ids')
    def _compute_ews1_status(self):
        """EWS1 status cascades from parent block to child units."""
        for rec in self:
            # If this is a unit in a block, inherit from parent
            if rec.parent_id and rec.parent_id.ews1_assessment_ids:
                latest = rec.parent_id.ews1_assessment_ids.sorted('assessment_date', reverse=True)[:1]
                if latest:
                    rec.ews1_status = 'pass' if latest.ews1_rating in ['A1', 'A2', 'A3'] else 'fail'
                else:
                    rec.ews1_status = 'pending'
            # If this is a block or standalone property
            elif rec.ews1_assessment_ids:
                latest = rec.ews1_assessment_ids.sorted('assessment_date', reverse=True)[:1]
                rec.ews1_status = 'pass' if latest.ews1_rating in ['A1', 'A2', 'A3'] else 'fail'
            else:
                # N/A for properties under 18m or not requiring EWS1
                rec.ews1_status = 'na' if rec.property_type != 'block' else 'pending'
```

### 4.4 Compliance Dashboard
- Expiring certificates view
- Non-compliant properties
- Upcoming inspections
- Compliance percentage by portfolio

### 4.5 Job Creation Wizard

- Bulk select properties due for inspection (14-30 day horizon)
- Auto-create field service jobs
- Match inspectors by skills
- Group by postcode for route efficiency

### 4.6 Property Asset Model

```python
class PropertyAsset(models.Model):
    _name = 'property_fielder.property.asset'
    _description = 'Property Asset (Appliance/Circuit)'
    _inherit = ['mail.thread']

    property_id = fields.Many2one('property_fielder.property', required=True)
    name = fields.Char(required=True)  # e.g., "Boiler", "Ring Main 1"
    barcode = fields.Char(string='Asset Barcode/QR')  # For scanning
    asset_type = fields.Selection([
        ('gas_appliance', 'Gas Appliance'),
        ('electrical_circuit', 'Electrical Circuit'),
        ('fire_door', 'Fire Door'),
        ('smoke_alarm', 'Smoke Alarm'),
        ('co_alarm', 'CO Alarm'),
        ('pat_appliance', 'PAT Appliance'),
    ])
    location = fields.Char()  # e.g., "Kitchen", "Hallway"
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    make = fields.Char()
    model = fields.Char()
    serial_number = fields.Char()
    install_date = fields.Date()
    last_service_date = fields.Date()
    next_service_date = fields.Date()
    active = fields.Boolean(default=True)
```

### 4.7 MEES Compliance Check (Future-Proofed)

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    mees_compliant = fields.Boolean(compute='_compute_mees', store=True)
    mees_exempt = fields.Boolean()
    mees_exempt_reason = fields.Selection([
        ('cost_cap', 'Cost Cap Exemption (£3,500)'),
        ('listed_building', 'Listed Building'),
        ('devaluation', 'Devaluation Exemption'),
        ('consent', 'Third Party Consent'),
        ('new_landlord', 'New Landlord Exemption'),
    ])
    mees_spend_cumulative = fields.Monetary(
        string='Cumulative Energy Efficiency Spend',
        help='Track spend towards £3,500 cost cap exemption'
    )

    @api.depends('epc_rating', 'mees_exempt')
    def _compute_mees(self):
        """
        MEES: Minimum rating required for letting.
        Uses system setting for future-proofing (E → C transition).
        """
        min_rating = self.env['ir.config_parameter'].sudo().get_param(
            'property_fielder.mees_min_rating', 'E'
        )
        valid_ratings = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        min_index = valid_ratings.index(min_rating)
        allowed = valid_ratings[:min_index + 1]

        for rec in self:
            if rec.mees_exempt:
                rec.mees_compliant = True
            else:
                rec.mees_compliant = rec.epc_rating in allowed
```

### 4.8 UPRN Validation

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    @api.constrains('uprn')
    def _check_uprn_format(self):
        """UPRN must be exactly 12 digits."""
        for rec in self:
            if rec.uprn:
                if not rec.uprn.isdigit() or len(rec.uprn) != 12:
                    raise ValidationError(
                        f"UPRN must be exactly 12 digits. Got: {rec.uprn}"
                    )

    @api.constrains('uprn')
    def _check_uprn_unique(self):
        """UPRN must be unique across all properties."""
        for rec in self:
            if rec.uprn:
                existing = self.search([
                    ('uprn', '=', rec.uprn),
                    ('id', '!=', rec.id),
                ], limit=1)
                if existing:
                    raise ValidationError(
                        f"UPRN {rec.uprn} already exists on property {existing.name}"
                    )
```

### 4.9 EPC Format Validation

```python
@api.constrains('epc_certificate_number')
def _check_epc_format(self):
    """EPC certificate number format: XXXX-XXXX-XXXX-XXXX-XXXX."""
    import re
    pattern = r'^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$'
    for rec in self:
        if rec.epc_certificate_number:
            if not re.match(pattern, rec.epc_certificate_number):
                raise ValidationError(
                    "EPC certificate number must be in format XXXX-XXXX-XXXX-XXXX-XXXX"
                )
```

**Note:** Right to Rent and Deposit Protection are now in `property_fielder_property_leasing` and `property_fielder_tenant_screening` modules respectively.

### 4.10 Certification Expiry Cron Job

```xml
<!-- data/ir_cron.xml -->
<record id="ir_cron_certification_expiry_check" model="ir.cron">
    <field name="name">Property Fielder: Check Certification Expiry</field>
    <field name="model_id" ref="model_property_fielder_certification"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_expiry_warnings()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

```python
class Certification(models.Model):
    _inherit = 'property_fielder.certification'

    def _cron_check_expiry_warnings(self):
        """Daily cron to update certification states and send warnings."""
        today = fields.Date.today()

        # Find certifications expiring within warning period
        certs = self.search([
            ('state', 'in', ['valid', 'expiring_soon']),
            ('expiry_date', '!=', False),
        ])

        for cert in certs:
            warning_days = cert.certification_type_id.warning_days or 30
            warning_date = cert.expiry_date - timedelta(days=warning_days)

            if cert.expiry_date < today:
                # Already expired
                cert.state = 'expired'
                cert._send_expiry_notification('expired')
            elif today >= warning_date:
                # Expiring soon
                if cert.state != 'expiring_soon':
                    cert.state = 'expiring_soon'
                    cert._send_expiry_notification('warning')

    def _send_expiry_notification(self, notification_type):
        """Send email notification for expiring/expired certificates."""
        template_ref = (
            'property_fielder_property_management.mail_template_cert_expired'
            if notification_type == 'expired'
            else 'property_fielder_property_management.mail_template_cert_warning'
        )
        template = self.env.ref(template_ref, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=False)

        # Also create activity for property manager
        self.property_id.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=self.expiry_date,
            summary=f"{self.certification_type_id.name} {'expired' if notification_type == 'expired' else 'expiring soon'}",
            note=f"Certificate {self.certificate_number} for {self.property_id.name}",
        )
```

---

## 5. UK Regulatory Compliance

| Regulation | Implementation |
|------------|----------------|
| **Gas Safety (I&U) Regs 1998** | CP12 annual renewal tracking |
| **Electrical Safety Standards 2020** | EICR 5-year tracking, C1/C2/C3/FI codes |
| **Fire Safety Act 2021** | Fire risk assessment for blocks |
| **EPC Regulations** | E minimum rating, exemption tracking |
| **HMO Licensing** | License expiry, max occupancy |
| **Selective Licensing** | Area-based licensing requirement |
| **Deposit Protection** | Moved to Leasing module |
| **Right to Rent** | Moved to Screening module |

---

## 6. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| FLAGE+ categories defined | ✅ Complete |
| Property states specified | ✅ Complete |
| Selective licensing added | ✅ Complete |
| **Property Asset model** | ✅ Added |
| **Key Set model (property_fielder.key.set)** | ✅ Added |
| **Access Code model** | ✅ Added |
| **Utility Meter model** | ✅ Added |
| **Meter Reading model** | ✅ Added |
| **Building Insurance model** | ✅ Added |
| **EWS1 Assessment model (Fire Safety Act)** | ✅ Added |
| **EWS1 cascade logic (Block → Units)** | ✅ Added |
| **HMO Room model (overcrowding compliance)** | ✅ Added |
| **HMO room size validation** | ✅ Added |
| **Council Tax account field** | ✅ Added |
| **income_account_id field** | ✅ Added |
| **Certification expiry cron job** | ✅ Added |
| **Expiry notification emails** | ✅ Added |
| **HMO status as Selection (not Boolean)** | ✅ Fixed |
| **HMO max occupancy field** | ✅ Added |
| **MEES future-proofed with config setting** | ✅ Added |
| **MEES cumulative spend tracking** | ✅ Added |
| **UPRN validation (12 digits, unique)** | ✅ Added |
| **EPC certificate number validation** | ✅ Added |
| **ir.attachment for certificates** | ✅ Fixed |
| **Right to Rent moved to Screening** | ✅ Fixed |
| **Deposit protection moved to Leasing** | ✅ Fixed |
| Compliance logic clear | ✅ Complete |
| **Overall** | ✅ Ready for Review |

