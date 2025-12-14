# PRD: Property Fielder Property Leasing

**Addon Name:** `property_fielder_property_leasing`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase A (Core Operations)  
**Effort:** 40-60 hours  

---

## 1. Overview

Lease and tenancy management with UK-specific requirements.

### 1.1 Purpose
Manage the full tenancy lifecycle from application through renewal or ending, including deposits, guarantors, and tenancy documentation.

### 1.2 Target Users
- Property Managers
- Landlords
- Tenants (via portal)

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for tenancy communication
    'account',  # Rent invoicing, deposit accounting
    'property_fielder_property_management',
    'property_fielder_tenant_screening',  # Right to Rent checks (referenced in 4.7)
]
```

---

## 3. Data Models

### 3.1 `property_fielder.tenancy`

**Inherits mail.thread for audit trail.**

```python
class Tenancy(models.Model):
    _name = 'property_fielder.tenancy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `tenant_ids` | Many2many → res.partner | Tenants |
| `lead_tenant_id` | Many2one → res.partner | Lead tenant |
| `tenancy_type` | Selection | ast/periodic/fixed/company |
| `start_date` | Date | Tenancy start |
| `end_date` | Date | Fixed term end |
| `rent_amount` | Monetary | **Monthly rent (Monetary field)** |
| `currency_id` | Many2one → res.currency | Currency |
| `rent_frequency` | Selection | **weekly/fortnightly/4_weekly/monthly** |
| `rent_due_day` | Integer | Day of month rent due |
| `deposit_amount` | Monetary | **Deposit amount (max 5 weeks)** |
| `deposit_scheme` | Selection | dps/tds/mydeposits |
| `deposit_reference` | Char | Scheme reference |
| `deposit_protected_date` | Date | Protection date |
| `guarantor_id` | Many2one → res.partner | Guarantor |
| `state` | Selection | draft/active/ending/ended/archived |
| `break_clause_date` | Date | Break clause date |
| `renewal_offered` | Boolean | Renewal offered |
| `renewal_date` | Date | Renewal offer date |
| `how_to_rent_delivered` | Date | Guide delivery date |
| `how_to_rent_version` | Char | **Version of How to Rent guide served** |
| `how_to_rent_attachment_id` | Many2one → ir.attachment | **Specific version served** |
| `epc_delivered` | Date | EPC delivery date |
| `gas_cert_delivered` | Date | Gas cert delivery date |
| `permitted_occupier_ids` | Many2many → res.partner | **Permitted occupiers (not on AST)** |

### 3.2 `property_fielder.tenancy.document`
Tenancy documentation tracking.

| Field | Type | Description |
|-------|------|-------------|
| `tenancy_id` | Many2one → tenancy | Tenancy |
| `document_type` | Selection | agreement/inventory/deposit_cert/how_to_rent/epc/gas_cert |
| `attachment_id` | Many2one → ir.attachment | **Document file (proper Odoo pattern)** |
| `filename` | Char | Filename |
| `issued_date` | Date | Issue date |
| `signed_date` | Date | Signed date |
| `tenant_signature_id` | Many2one → signature | Tenant signature |
| `landlord_signature_id` | Many2one → signature | Landlord signature |

### 3.3 `property_fielder.deposit`
Deposit protection tracking.

| Field | Type | Description |
|-------|------|-------------|
| `tenancy_id` | Many2one → tenancy | Tenancy |
| `amount` | Monetary | **Deposit amount (Monetary field)** |
| `scheme` | Selection | dps/tds/mydeposits |
| `scheme_reference` | Char | Scheme reference |
| `protected_date` | Date | Protection date (must be within 30 days) |
| `prescribed_info_date` | Date | PI served date |
| `state` | Selection | pending/protected/returned/disputed |
| `return_amount` | Monetary | Amount returned |
| `deductions` | Monetary | Deductions |
| `currency_id` | Many2one → res.currency | **Currency** |
| `deduction_reason` | Text | Reason for deductions |

---

## 4. Key Features

### 4.1 Tenancy Lifecycle
- Draft → Active → Periodic → Ending → Ended
- Automatic periodic conversion after fixed term
- Break clause tracking
- Renewal workflow

### 4.2 UK Deposit Protection
- 30-day protection deadline tracking
- Prescribed Information serving
- Integration with DPS/TDS/MyDeposits APIs (future)
- Section 21 blocking if not protected

### 4.3 Required Documentation
- How to Rent Guide (current version)
- EPC certificate
- Gas Safety Certificate
- Tenancy Agreement
- Deposit Certificate

### 4.4 Guarantor Management
- Guarantor contact details
- Guarantor agreement tracking
- Notification on arrears

### 4.5 Rent Schedule Generation

```python
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    rent_schedule_ids = fields.One2many('property_fielder.rent.schedule', 'tenancy_id')

    def _get_safe_due_date(self, year, month, preferred_day):
        """
        Get safe due date handling end-of-month edge cases.
        E.g., if rent_due_day=31 and month=February, returns Feb 28/29.
        """
        max_day = monthrange(year, month)[1]
        safe_day = min(preferred_day, max_day)
        return date(year, month, safe_day)

    def action_generate_rent_schedule(self):
        """Generate rent schedule for tenancy term with safe date handling."""
        for rec in self:
            current_date = rec.start_date
            end_date = rec.end_date or rec.start_date + relativedelta(years=1)

            while current_date <= end_date:
                # Use safe date calculation to avoid ValueError on Feb 31, etc.
                due_date = rec._get_safe_due_date(
                    current_date.year,
                    current_date.month,
                    rec.rent_due_day
                )

                self.env['property_fielder.rent.schedule'].create({
                    'tenancy_id': rec.id,
                    'due_date': due_date,
                    'amount': rec.rent_amount,
                    'state': 'pending',
                })

                if rec.rent_frequency == 'monthly':
                    current_date += relativedelta(months=1)
                elif rec.rent_frequency == 'weekly':
                    current_date += relativedelta(weeks=1)
                elif rec.rent_frequency == '4_weekly':
                    # 4-weekly = 13 payments per year (common for Universal Credit tenants)
                    current_date += relativedelta(weeks=4)
                else:  # fortnightly
                    current_date += relativedelta(weeks=2)
```

### 4.6 Rent Schedule Model

| Field | Type | Description |
|-------|------|-------------|
| `tenancy_id` | Many2one → tenancy | Tenancy |
| `due_date` | Date | Payment due date |
| `amount` | Monetary | Amount due |
| `currency_id` | Many2one → res.currency | Currency |
| `state` | Selection | pending/paid/partial/overdue |
| `payment_date` | Date | Actual payment date |
| `payment_amount` | Monetary | Amount paid |
| `invoice_id` | Many2one → account.move | Linked invoice |
| `is_invoiced` | Boolean | **Invoice generated flag** |
| `payment_id` | Many2one → account.payment | **Direct payment (if no invoice)** |

### 4.7 Automatic Invoice Generation (Cron)

```python
class RentSchedule(models.Model):
    _name = 'property_fielder.rent.schedule'

    @api.model
    def _cron_generate_rent_invoices(self):
        """
        Scheduled Action: Generate rent invoices 7 days before due date.
        Run daily at 6:00 AM.
        """
        target_date = fields.Date.today() + relativedelta(days=7)
        schedules = self.search([
            ('due_date', '=', target_date),
            ('is_invoiced', '=', False),
            ('tenancy_id.state', '=', 'active'),
        ])

        for schedule in schedules:
            tenancy = schedule.tenancy_id
            property_rec = tenancy.property_id

            # Generate payment reference for bank reconciliation
            # Format: SURNAME-PROPREF (e.g., "SMITH-123ABC")
            payment_ref = f"{tenancy.lead_tenant_id.name.split()[-1][:10].upper()}-{property_rec.ref or property_rec.id}"

            # Get applicable taxes (UK residential rent is usually VAT exempt)
            tax_ids = property_rec.rent_tax_ids.ids if property_rec.rent_tax_ids else []

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': tenancy.lead_tenant_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_date_due': schedule.due_date,
                'payment_reference': payment_ref,  # For bank reconciliation
                'invoice_line_ids': [(0, 0, {
                    'name': f"Rent: {property_rec.name} ({schedule.due_date})",
                    'quantity': 1,
                    'price_unit': schedule.amount,
                    'account_id': property_rec.income_account_id.id or \
                        self.env.ref('property_fielder_property_leasing.rent_income_account').id,
                    'tax_ids': [(6, 0, tax_ids)],  # Apply property-specific taxes
                })],
            })
            schedule.write({
                'invoice_id': invoice.id,
                'is_invoiced': True,
            })
            invoice.action_post()
```

**Scheduled Action XML:**
```xml
<record id="ir_cron_generate_rent_invoices" model="ir.cron">
    <field name="name">Generate Rent Invoices</field>
    <field name="model_id" ref="model_property_fielder_rent_schedule"/>
    <field name="state">code</field>
    <field name="code">model._cron_generate_rent_invoices()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="nextcall" eval="datetime.now().replace(hour=6, minute=0)"/>
</record>
```

### 4.8 Right to Rent

**Note:** Right to Rent is managed in `property_fielder_tenant_screening` addon.

This addon tracks:
- Right to Rent check completed (Boolean)
- Check date
- Follow-up date (for time-limited permissions)

### 4.8 AST QWeb Template

**Tenancy Agreement PDF generation from Odoo data:**

```xml
<!-- reports/report_tenancy_agreement.xml -->
<template id="report_tenancy_agreement_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="tenancy">
            <t t-call="web.external_layout">
                <div class="page">
                    <h1 class="text-center">ASSURED SHORTHOLD TENANCY AGREEMENT</h1>

                    <h3>1. PARTIES</h3>
                    <p><strong>Landlord:</strong> <t t-esc="tenancy.property_id.owner_id.name"/></p>
                    <p><strong>Tenant(s):</strong>
                        <t t-foreach="tenancy.tenant_ids" t-as="tenant">
                            <t t-esc="tenant.name"/><t t-if="not tenant_last">, </t>
                        </t>
                    </p>

                    <h3>2. PROPERTY</h3>
                    <p><t t-esc="tenancy.property_id.street"/>,
                       <t t-esc="tenancy.property_id.city"/>,
                       <t t-esc="tenancy.property_id.zip"/></p>

                    <h3>3. TERM</h3>
                    <p>Fixed term from <t t-esc="tenancy.start_date"/> to <t t-esc="tenancy.end_date"/></p>

                    <h3>4. RENT</h3>
                    <p><t t-esc="tenancy.rent_amount" t-options="{'widget': 'monetary'}"/>
                       payable <t t-esc="tenancy.rent_frequency"/></p>

                    <h3>5. DEPOSIT</h3>
                    <p><t t-esc="tenancy.deposit_amount" t-options="{'widget': 'monetary'}"/>
                       protected with <t t-esc="tenancy.deposit_scheme"/></p>

                    <!-- Additional clauses... -->

                    <div class="signature-section mt-5">
                        <div class="row">
                            <div class="col-6">
                                <p>Landlord Signature: _______________</p>
                                <p>Date: _______________</p>
                            </div>
                            <div class="col-6">
                                <p>Tenant Signature: _______________</p>
                                <p>Date: _______________</p>
                            </div>
                        </div>
                    </div>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 4.9 Holding Deposit (Tenant Fees Act 2019)

| Field | Type | Description |
|-------|------|-------------|
| `holding_deposit_amount` | Monetary | Max 1 week's rent |
| `holding_deposit_date` | Date | Date received |
| `holding_deposit_deadline` | Date | 15-day deadline |
| `holding_deposit_outcome` | Selection | applied/returned/forfeited |
| `holding_deposit_forfeiture_reason` | Selection | failed_rtr/false_info/withdrew |

---

## 5. UK Regulatory Compliance

| Regulation | Implementation |
|------------|----------------|
| **Tenant Fees Act 2019** | Deposit cap (5 weeks rent if <£50k pa) |
| **Housing Act 2004** | Deposit protection within 30 days |
| **Prescribed Information** | Serve within 30 days, track date |
| **Right to Rent** | ID verification, follow-up checks |
| **How to Rent Guide** | Track delivery, current version |
| **Section 21** | Block if compliance not met |

### 5.1 Section 21 Eviction Blocking

```python
class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    section_21_valid = fields.Boolean(compute='_compute_section_21_valid')
    section_21_blockers = fields.Text(compute='_compute_section_21_valid')

    @api.depends('deposit_protected_date', 'how_to_rent_delivered',
                 'epc_delivered', 'gas_cert_delivered')
    def _compute_section_21_valid(self):
        for rec in self:
            blockers = []
            if not rec.deposit_protected_date:
                blockers.append('Deposit not protected')
            if not rec.how_to_rent_delivered:
                blockers.append('How to Rent not delivered')
            if not rec.epc_delivered:
                blockers.append('EPC not provided')
            if not rec.gas_cert_delivered:
                blockers.append('Gas cert not provided')
            rec.section_21_valid = len(blockers) == 0
            rec.section_21_blockers = ', '.join(blockers) if blockers else None
```

---

## 6. Deposit Cap Validation

### 6.1 Tenant Fees Act 2019 Compliance

```python
class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    @api.constrains('deposit_amount', 'rent_amount', 'rent_frequency')
    def _check_deposit_cap(self):
        """
        Tenant Fees Act 2019:
        - Deposit max 5 weeks rent if annual rent < £50,000
        - Deposit max 6 weeks rent if annual rent >= £50,000
        """
        for rec in self:
            if rec.rent_frequency == 'monthly':
                annual_rent = rec.rent_amount * 12
                weekly_rent = rec.rent_amount * 12 / 52
            elif rec.rent_frequency == 'weekly':
                annual_rent = rec.rent_amount * 52
                weekly_rent = rec.rent_amount
            else:  # fortnightly
                annual_rent = rec.rent_amount * 26
                weekly_rent = rec.rent_amount / 2

            max_weeks = 6 if annual_rent >= 50000 else 5
            max_deposit = weekly_rent * max_weeks

            if rec.deposit_amount > max_deposit:
                raise ValidationError(
                    f"Deposit £{rec.deposit_amount:.2f} exceeds {max_weeks} weeks rent "
                    f"(max £{max_deposit:.2f}). Tenant Fees Act 2019."
                )
```

---

## 7. Rent History Tracking

### 7.1 Rent Change Model

Track rent increases during periodic tenancies (Section 13 notices).

```python
class RentChange(models.Model):
    _name = 'property_fielder.rent.change'
    _description = 'Rent Change History'
    _order = 'effective_date desc'

    tenancy_id = fields.Many2one('property_fielder.tenancy', required=True, ondelete='cascade')
    previous_amount = fields.Monetary(string='Previous Rent')
    new_amount = fields.Monetary(string='New Rent')
    currency_id = fields.Many2one('res.currency')
    effective_date = fields.Date(string='Effective From', required=True)
    notice_served_date = fields.Date(string='Section 13 Notice Served')
    notice_type = fields.Selection([
        ('section_13', 'Section 13 (Periodic)'),
        ('renewal', 'Renewal Agreement'),
        ('mutual', 'Mutual Agreement'),
    ])
    attachment_id = fields.Many2one('ir.attachment', string='Notice Document')

class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    rent_change_ids = fields.One2many('property_fielder.rent.change', 'tenancy_id')

    def action_increase_rent(self):
        """Open wizard to record rent increase."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Rent Increase',
            'res_model': 'property_fielder.rent.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tenancy_id': self.id,
                'default_previous_amount': self.rent_amount,
            },
        }


class RentChangeWizard(models.TransientModel):
    _name = 'property_fielder.rent.change.wizard'
    _description = 'Rent Change Wizard'

    tenancy_id = fields.Many2one('property_fielder.tenancy', required=True)
    previous_amount = fields.Monetary(readonly=True)
    new_amount = fields.Monetary(required=True)
    currency_id = fields.Many2one('res.currency')
    effective_date = fields.Date(required=True)
    notice_type = fields.Selection([
        ('section_13', 'Section 13 (Periodic)'),
        ('renewal', 'Renewal Agreement'),
        ('mutual', 'Mutual Agreement'),
    ], required=True)

    def action_confirm(self):
        """Apply rent change and update future schedule lines."""
        self.ensure_one()

        # Create rent change record
        self.env['property_fielder.rent.change'].create({
            'tenancy_id': self.tenancy_id.id,
            'previous_amount': self.previous_amount,
            'new_amount': self.new_amount,
            'effective_date': self.effective_date,
            'notice_type': self.notice_type,
        })

        # Update tenancy rent amount
        self.tenancy_id.rent_amount = self.new_amount

        # Update future pending rent schedule lines
        future_schedules = self.env['property_fielder.rent.schedule'].search([
            ('tenancy_id', '=', self.tenancy_id.id),
            ('due_date', '>=', self.effective_date),
            ('state', '=', 'pending'),
            ('is_invoiced', '=', False),
        ])
        future_schedules.write({'amount': self.new_amount})

        return {'type': 'ir.actions.act_window_close'}
```

---

## 8. Occupancy Constraint

Prevent overcrowding by validating tenant count against property capacity.

### 8.1 Permitted Occupier Model

```python
class PermittedOccupier(models.Model):
    _name = 'property_fielder.permitted.occupier'
    _description = 'Permitted Occupier (not on AST)'

    tenancy_id = fields.Many2one('property_fielder.tenancy', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Person')
    name = fields.Char(string='Name', required=True)
    date_of_birth = fields.Date(string='Date of Birth', help="Required for Housing Act 1985 overcrowding calculation")
    relationship = fields.Selection([
        ('child', 'Child'),
        ('spouse', 'Spouse/Partner'),
        ('parent', 'Parent'),
        ('other', 'Other Family'),
    ])
    is_child = fields.Boolean(compute='_compute_is_child', store=True)

    @api.depends('date_of_birth')
    def _compute_is_child(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_of_birth:
                age = (today - rec.date_of_birth).days // 365
                rec.is_child = age < 10  # Under 10 counts as 0.5 for room standard
            else:
                rec.is_child = False
```

### 8.2 Occupancy Calculation (Housing Act 1985)

```python
class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    permitted_occupier_ids = fields.One2many(
        'property_fielder.permitted.occupier', 'tenancy_id',
        string='Permitted Occupiers'
    )
    occupant_count = fields.Integer(
        compute='_compute_occupant_count',
        store=True,
        help="Total number of occupants including tenants and permitted occupiers"
    )
    occupant_count_room_standard = fields.Float(
        compute='_compute_occupant_count',
        store=True,
        help="Room standard count (children under 10 = 0.5)"
    )

    @api.depends('tenant_ids', 'permitted_occupier_ids', 'permitted_occupier_ids.is_child')
    def _compute_occupant_count(self):
        for rec in self:
            tenant_count = len(rec.tenant_ids)
            adult_occupiers = len(rec.permitted_occupier_ids.filtered(lambda o: not o.is_child))
            child_occupiers = len(rec.permitted_occupier_ids.filtered(lambda o: o.is_child))

            rec.occupant_count = tenant_count + adult_occupiers + child_occupiers
            # Room standard: children under 10 count as 0.5
            rec.occupant_count_room_standard = tenant_count + adult_occupiers + (child_occupiers * 0.5)

    @api.constrains('tenant_ids', 'permitted_occupier_ids')
    def _check_occupancy(self):
        """
        Ensure occupancy does not exceed property capacity.
        Housing Act 1985 Room Standard: Children under 10 count as 0.5.
        """
        for rec in self:
            max_occupancy = rec.property_id.max_occupancy or 0
            if max_occupancy and rec.occupant_count_room_standard > max_occupancy:
                raise ValidationError(
                    f"Occupancy ({rec.occupant_count_room_standard:.1f} room standard) "
                    f"exceeds property maximum ({max_occupancy}). "
                    "This may constitute overcrowding under Housing Act 1985."
                )
```

---

## 9. Overlapping Tenancy Prevention

```python
class Tenancy(models.Model):
    _inherit = 'property_fielder.tenancy'

    @api.constrains('property_id', 'start_date', 'end_date', 'state')
    def _check_no_overlap(self):
        """Prevent overlapping active tenancies (except HMO room-level)."""
        for rec in self:
            if rec.state not in ['active', 'draft']:
                continue
            if rec.property_id.is_hmo:
                continue  # HMOs allow multiple tenancies (room-level)

            domain = [
                ('property_id', '=', rec.property_id.id),
                ('id', '!=', rec.id),
                ('state', 'in', ['active', 'draft']),
                ('start_date', '<=', rec.end_date or fields.Date.max),
            ]
            if rec.end_date:
                domain.append(('end_date', '>=', rec.start_date))
            else:
                domain.append('|')
                domain.append(('end_date', '>=', rec.start_date))
                domain.append(('end_date', '=', False))

            if self.search_count(domain):
                raise ValidationError(
                    f"Property {rec.property_id.name} already has an active tenancy "
                    "during this period. Only HMOs support multiple concurrent tenancies."
                )
```

---

## 11. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **tenant_screening dependency added** | ✅ Fixed |
| **Safe date handling (Feb 31 fix)** | ✅ Fixed |
| **is_invoiced field added** | ✅ Added |
| **Invoicing cron job defined** | ✅ Added |
| **Rent history tracking** | ✅ Added |
| **Rent change wizard** | ✅ Added |
| **Rent change updates future schedules** | ✅ Added |
| **permitted_occupier_ids field** | ✅ Added |
| **how_to_rent_version tracking** | ✅ Added |
| **how_to_rent_attachment_id** | ✅ Added |
| **Occupancy constraint** | ✅ Added |
| **Overlapping tenancy prevention** | ✅ Added |
| **mail.thread inheritance** | ✅ Added |
| **account dependency** | ✅ Added |
| **ir.attachment for documents** | ✅ Fixed |
| **Monetary fields on deposit** | ✅ Fixed |
| **Deposit cap validation** | ✅ Added |
| **Rent schedule generation** | ✅ Added |
| **Holding deposit tracking** | ✅ Added |
| **Right to Rent moved to screening** | ✅ Clarified |
| **4-weekly frequency (Universal Credit)** | ✅ Added |
| **payment_reference for bank reconciliation** | ✅ Added |
| **tax_ids in invoice creation** | ✅ Added |
| **PermittedOccupier model with DOB** | ✅ Added |
| **Housing Act 1985 room standard (0.5 for <10)** | ✅ Added |
| **AST QWeb template placeholder** | ✅ Added |
| Uses Monetary fields | ✅ Complete |
| UK compliance covered | ✅ Complete |
| Deposit protection clear | ✅ Complete |
| Section 21 blocking logic | ✅ Complete |
| Documentation tracked | ✅ Complete |
| **Overall** | ✅ Build Ready (90%+) |

