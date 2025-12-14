# PRD: Property Fielder Insurance Management

**Addon Name:** `property_fielder_insurance_management`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase D (Advanced Features)  
**Effort:** 20-30 hours  

---

## 1. Overview

Insurance policy tracking, renewals, and claims management.

### 1.1 Purpose
Track all property-related insurance policies including buildings, contents, landlord, and rent guarantee with renewal reminders and claims handling.

### 1.2 Target Users
- Property Managers
- Landlords
- Finance Team

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for policy/claim tracking
    'account',  # Premium bills, claim settlements
    'property_fielder_property_management',
    'property_fielder_property_maintenance',  # Link claims to maintenance
]
```

---

## 3. Data Models

### 3.1 `property_fielder.insurance.policy`

**Inherits mail.thread for audit trail.**

```python
class InsurancePolicy(models.Model):
    _name = 'property_fielder.insurance.policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

| Field | Type | Description |
|-------|------|-------------|
| `property_ids` | Many2many → property | **Properties (supports portfolio policies)** |
| `property_id` | Many2one → property | Property (single, for backward compat) |
| `tenancy_id` | Many2one → tenancy | **Tenancy (for Rent Guarantee)** |
| `policy_type` | Selection | buildings/contents/landlord/rent_guarantee/legal |
| `provider_id` | Many2one → res.partner | **Insurance provider (res.partner)** |
| `broker_id` | Many2one → res.partner | **Broker (arranges policy)** |
| `underwriter` | Char | **Underwriter/Carrier name** |
| `policy_number` | Char | Policy number |
| `coverage_amount` | Monetary | **Sum insured (Monetary)** |
| `liability_limit` | Monetary | **Public Liability limit (for HMO validation)** |
| `excess` | Monetary | **Excess amount (Monetary)** |
| `excess_payer` | Selection | **landlord/tenant (who pays excess)** |
| `premium_net` | Monetary | **Net premium before IPT** |
| `ipt_amount` | Monetary | **Insurance Premium Tax (12%)** |
| `premium_annual` | Monetary | **Total annual premium (net + IPT)** |
| `currency_id` | Many2one → res.currency | Currency |
| `payment_frequency` | Selection | annual/monthly |
| `start_date` | Date | Policy start |
| `end_date` | Date | Policy end |
| `renewal_date` | Date | Renewal date |
| `auto_renew` | Boolean | Auto-renewal |
| `state` | Selection | active/expired/cancelled |
| `attachment_ids` | Many2many → ir.attachment | **Policy documents (schedule, cert, wording)** |
| `ipid_document_id` | Many2one → ir.attachment | **FCA: Insurance Product Info Document** |
| `statement_of_facts_id` | Many2one → ir.attachment | **FCA: Statement of Facts document** |
| `premium_invoice_id` | Many2one → account.move | **Premium vendor bill** |
| `is_rechargeable` | Boolean | **Recharge premium to tenant** |
| `recharge_percentage` | Float | **% of premium to recharge (default 100)** |
| `notes` | Text | Policy notes |

### 3.2 `property_fielder.insurance.claim`

Insurance claim.

| Field | Type | Description |
|-------|------|-------------|
| `policy_id` | Many2one → policy | Policy |
| `property_id` | Many2one → property | Property |
| `maintenance_id` | Many2one → maintenance.request | **Linked maintenance request** |
| `claim_date` | Date | Claim date |
| `incident_date` | Date | Incident date |
| `claim_reference` | Char | Insurer claim reference |
| `claim_type` | Selection | damage/theft/liability/rent_loss/other |
| `description` | Text | Claim description |
| `claim_amount` | Monetary | **Claimed amount (Monetary)** |
| `excess_paid` | Monetary | **Excess paid (Monetary)** |
| `excess_payer` | Selection | **landlord/tenant** |
| `settled_amount` | Monetary | **Settlement amount (Monetary)** |
| `repair_cost` | Monetary | **Actual repair cost** |
| `shortfall` | Monetary | **Repair cost - settlement (computed)** |
| `state` | Selection | submitted/in_progress/approved/rejected/paid |
| `settled_date` | Date | Settlement date |
| `settlement_invoice_id` | Many2one → account.move | **Settlement credit note** |
| `photo_ids` | Many2many → ir.attachment | Evidence photos |
| `document_ids` | Many2many → ir.attachment | Supporting documents |
| `currency_id` | Many2one → res.currency | Currency |

### 3.3 `property_fielder.insurance.gap`

Insurance gap record (computed).

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `gap_type` | Selection | buildings/contents/landlord/rent_guarantee |
| `reason` | Char | Why gap exists |
| `severity` | Selection | critical/warning/info |

---

## 4. Key Features

### 4.1 Policy Tracking
- All policy types per property
- Coverage details
- Premium tracking
- Document storage

### 4.2 Renewal Management
- 30/60/90 day renewal reminders
- Renewal quote comparison
- Lapse prevention alerts

### 4.3 Claims Management
- Claim submission workflow
- Evidence attachment
- Status tracking
- Settlement recording

### 4.4 Reporting
- Policies expiring
- Premium costs by property
- Claims history
- Coverage gaps

### 4.5 Coverage Gap Detection (Leasehold-Aware)

**UK Leasehold: Buildings insurance is often held by Freeholder/Block Management.**

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    is_block_insured = fields.Boolean(
        string='Block Insured',
        help="Buildings insurance held by Freeholder/Block Management"
    )
    insurance_gap_ids = fields.One2many(
        'property_fielder.insurance.gap',
        'property_id',
        compute='_compute_insurance_gaps',
        store=True
    )

    @api.depends('insurance_policy_ids.state', 'insurance_policy_ids.policy_type',
                 'is_block_insured', 'furnishing_state')
    def _compute_insurance_gaps(self):
        """Detect missing required insurance coverage."""
        for rec in self:
            gaps = []

            # Buildings insurance (skip if block insured)
            if not rec.is_block_insured:
                if 'buildings' not in rec._active_policy_types():
                    gaps.append({
                        'gap_type': 'buildings',
                        'reason': 'No active buildings insurance',
                        'severity': 'critical',
                    })

            # Landlord liability (always required)
            if 'landlord' not in rec._active_policy_types():
                gaps.append({
                    'gap_type': 'landlord',
                    'reason': 'No active landlord liability insurance',
                    'severity': 'critical',
                })

            # Contents (required if furnished)
            if rec.furnishing_state == 'furnished':
                if 'contents' not in rec._active_policy_types():
                    gaps.append({
                        'gap_type': 'contents',
                        'reason': 'Furnished property without contents insurance',
                        'severity': 'warning',
                    })

            # Rent Guarantee (recommended if tenanted)
            if rec.tenancy_ids.filtered(lambda t: t.state == 'active'):
                if 'rent_guarantee' not in rec._active_policy_types():
                    gaps.append({
                        'gap_type': 'rent_guarantee',
                        'reason': 'Active tenancy without rent guarantee',
                        'severity': 'info',
                    })

            rec.insurance_gap_ids = [(5, 0, 0)] + [(0, 0, g) for g in gaps]

    def _active_policy_types(self):
        return self.insurance_policy_ids.filtered(
            lambda p: p.state == 'active'
        ).mapped('policy_type')
```

### 4.6 Portfolio Policy Support

**One Policy → Many Properties (UK Portfolio Landlords):**

```python
class InsurancePolicy(models.Model):
    _inherit = 'property_fielder.insurance.policy'

    property_ids = fields.Many2many(
        'property_fielder.property',
        string='Covered Properties',
        help="Portfolio policy covering multiple properties"
    )
    property_count = fields.Integer(compute='_compute_property_count')

    @api.depends('property_ids')
    def _compute_property_count(self):
        for rec in self:
            rec.property_count = len(rec.property_ids)

    @api.depends('premium_net')
    def _compute_ipt(self):
        """Insurance Premium Tax (12% standard rate in UK)."""
        for rec in self:
            rec.ipt_amount = rec.premium_net * 0.12
            rec.premium_annual = rec.premium_net + rec.ipt_amount
```

### 4.7 HMO Liability Validation

```python
class InsurancePolicy(models.Model):
    _inherit = 'property_fielder.insurance.policy'

    @api.constrains('liability_limit', 'property_ids')
    def _check_hmo_liability(self):
        """HMO licensing often requires minimum £5M public liability."""
        for rec in self:
            if rec.policy_type == 'landlord':
                hmo_properties = rec.property_ids.filtered(
                    lambda p: p.is_hmo or p.hmo_status == 'licensed'
                )
                if hmo_properties and rec.liability_limit < 5000000:
                    raise ValidationError(
                        f"HMO properties require minimum £5,000,000 public liability. "
                        f"Current limit: £{rec.liability_limit:,.0f}"
                    )
```

### 4.8 Financial Integration

```python
class InsurancePolicy(models.Model):
    _inherit = 'property_fielder.insurance.policy'

    def action_create_premium_bill(self):
        """Create vendor bill for premium payment (split net/IPT)."""
        self.ensure_one()
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.broker_id.id or self.provider_id.id,
            'invoice_date': self.start_date,
            'invoice_line_ids': [
                (0, 0, {
                    'name': f'Insurance Premium (Net): {self.policy_number}',
                    'quantity': 1,
                    'price_unit': self.premium_net,
                }),
                (0, 0, {
                    'name': f'Insurance Premium Tax (IPT): {self.policy_number}',
                    'quantity': 1,
                    'price_unit': self.ipt_amount,
                }),
            ],
        })
        self.premium_invoice_id = bill.id
        return bill

    def action_recharge_tenant(self):
        """Recharge insurance premium to tenant (Commercial/some ASTs)."""
        self.ensure_one()
        if not self.is_rechargeable or not self.tenancy_id:
            raise UserError("Policy is not rechargeable or has no linked tenancy.")

        recharge_amount = self.premium_annual * (self.recharge_percentage / 100)
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.tenancy_id.tenant_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Insurance Recharge: {self.policy_number}',
                'quantity': 1,
                'price_unit': recharge_amount,
            })],
        })
        return invoice


class InsuranceClaim(models.Model):
    _inherit = 'property_fielder.insurance.claim'

    @api.depends('settled_amount', 'repair_cost')
    def _compute_shortfall(self):
        for rec in self:
            rec.shortfall = (rec.repair_cost or 0) - (rec.settled_amount or 0)

    def action_record_settlement(self):
        """Record settlement as credit note/payment."""
        self.ensure_one()
        if self.settled_amount:
            # Create credit note for settlement
            credit = self.env['account.move'].create({
                'move_type': 'in_refund',
                'partner_id': self.policy_id.provider_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f'Insurance Settlement: {self.claim_reference}',
                    'quantity': 1,
                    'price_unit': self.settled_amount,
                })],
            })
            self.settlement_invoice_id = credit.id
            self.state = 'paid'
```

### 4.7 Rent Guarantee Validity Check

**Rent Guarantee policies require passed tenant reference:**

```python
class InsurancePolicy(models.Model):
    _inherit = 'property_fielder.insurance.policy'

    @api.constrains('policy_type', 'tenancy_id')
    def _check_rent_guarantee_validity(self):
        for rec in self:
            if rec.policy_type == 'rent_guarantee':
                if not rec.tenancy_id:
                    raise ValidationError(
                        "Rent Guarantee policy must be linked to a tenancy"
                    )
                # Check tenant passed referencing
                application = self.env['property_fielder.tenant.application'].search([
                    ('tenancy_id', '=', rec.tenancy_id.id),
                    ('state', '=', 'approved'),
                ], limit=1)
                if not application:
                    raise ValidationError(
                        "Rent Guarantee requires approved tenant reference"
                    )
```

### 4.6 Claim Evidence Requirements

| Claim Type | Required Evidence |
|------------|-------------------|
| Damage | Photos, contractor quote, police report (if vandalism) |
| Theft | Police report, photos, inventory list |
| Rent Loss | Tenancy agreement, arrears statement, eviction notice |
| Liability | Incident report, medical records, witness statements |

---

## 5. UK Insurance Types

| Policy Type | Purpose |
|-------------|---------|
| **Buildings** | Structure, fixtures, fittings |
| **Contents** | Landlord's furniture/appliances |
| **Landlord** | Combined buildings + liability |
| **Rent Guarantee** | Covers rent arrears |
| **Legal Expenses** | Eviction, disputes |

### 5.1 Renewal Reminder Workflow

```python
class InsurancePolicy(models.Model):
    _inherit = 'property_fielder.insurance.policy'

    @api.model
    def _cron_renewal_reminders(self):
        """Send renewal reminders at 90, 60, 30 days."""
        today = fields.Date.today()
        for days in [90, 60, 30]:
            expiring = self.search([
                ('end_date', '=', today + timedelta(days=days)),
                ('state', '=', 'active'),
            ])
            for policy in expiring:
                policy._send_renewal_reminder(days)
```

---

## 6. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **broker_id added** | ✅ Added |
| **tenancy_id for Rent Guarantee** | ✅ Added |
| **attachment_ids (Many2many)** | ✅ Fixed |
| **is_block_insured flag** | ✅ Added |
| **account dependency** | ✅ Added |
| **maintenance_id on claims** | ✅ Added |
| **Gap model defined** | ✅ Added |
| **Leasehold-aware gap detection** | ✅ Added |
| **Financial integration (bills/settlements)** | ✅ Added |
| **Rent Guarantee validity check** | ✅ Added |
| **excess_payer field** | ✅ Added |
| **mail.thread inheritance** | ✅ Added |
| **Provider as res.partner** | ✅ Fixed |
| **Monetary fields** | ✅ Fixed |
| **Coverage gap detection** | ✅ Added |
| **Claim evidence requirements** | ✅ Added |
| **Portfolio policy (Many2many properties)** | ✅ Added |
| **liability_limit for HMO validation** | ✅ Added |
| **IPT (Insurance Premium Tax) fields** | ✅ Added |
| **Tenant recharge mechanism** | ✅ Added |
| **IPID document field (FCA)** | ✅ Added |
| Uses ir.attachment | ✅ Complete |
| Policy types defined | ✅ Complete |
| Claims workflow clear | ✅ Complete |
| Renewal tracking | ✅ Complete |
| **Overall** | ✅ Ready for Review |

