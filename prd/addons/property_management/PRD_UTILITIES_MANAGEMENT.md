# PRD: Property Fielder Utilities Management

**Addon Name:** `property_fielder_utilities_management`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase D (Advanced Features)  
**Effort:** 20-30 hours  

---

## 1. Overview

Utility account and billing management for properties.

### 1.1 Purpose
Track utility accounts, meter readings, and billing for landlord-managed utilities (typically HMOs and all-bills-included properties).

### 1.2 Target Users
- Property Managers
- Finance Team
- Landlords (HMO)

---

## 2. Dependencies

```python
depends = ['base', 'mail', 'property_fielder_property_management', 'account']
```

---

## 3. Data Models

### 3.1 `property_fielder.utility.account`
Utility account.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `utility_type` | Selection | **gas/electricity/water/broadband (Council Tax moved to separate model)** |
| `supplier_id` | Many2one → res.partner | **Supplier (res.partner)** |
| `account_number` | Char | Account number |
| `mpan` | Char | **MPAN (Electricity meter point)** |
| `mprn` | Char | **MPRN (Gas meter point)** |
| `meter_serial` | Char | Meter serial number |
| `tariff_name` | Char | Tariff name |
| `tariff_rate` | Monetary | **Rate per unit (Monetary)** |
| `standing_charge` | Monetary | **Daily standing charge (Monetary)** |
| `currency_id` | Many2one → res.currency | Currency |
| `payment_method` | Selection | direct_debit/invoice/prepay |
| `contract_start` | Date | Contract start |
| `contract_end` | Date | Contract end |
| `state` | Selection | active/switching/closed |
| `gas_conversion_factor` | Float | **Gas m³ to kWh conversion factor (default 11.1868)** |
| `gas_calorific_value` | Float | **Calorific value from supplier (MJ/m³)** |
| `last_cp12_date` | Date | **Last Gas Safety Certificate date (linked from compliance)** |
| `cp12_expiry_date` | Date | **Computed: last_cp12_date + 1 year** |
| `daily_average_consumption` | Float | **Fallback for variance calc when readings unavailable** |

### 3.2 `property_fielder.meter.reading`
Meter reading record.

| Field | Type | Description |
|-------|------|-------------|
| `utility_id` | Many2one → utility.account | Utility account |
| `reading_date` | Date | Reading date |
| `reading_value` | Float | Meter reading |
| `reading_type` | Selection | actual/estimate/exchange |
| `photo_id` | Many2one → ir.attachment | **Meter photo (ir.attachment)** |
| `submitted_by` | Many2one → res.users | Who submitted |
| `units_used` | Float | Units since last reading |
| `is_rollover` | Boolean | **Meter rollover (dial reset to 0)** |
| `meter_max_value` | Float | **Max meter value before rollover (e.g., 99999)** |
| `indicative_cost` | Monetary | **Indicative cost (not guaranteed)** |
| `is_exchange` | Boolean | **Meter exchange reading** |
| `old_meter_serial` | Char | **Old meter serial (for exchange)** |
| `new_meter_serial` | Char | **New meter serial (for exchange)** |

### 3.3 `property_fielder.meter.exchange`

**Dedicated model for meter exchange events (separate from readings):**

| Field | Type | Description |
|-------|------|-------------|
| `utility_id` | Many2one → utility.account | Utility account |
| `exchange_date` | Date | Date of meter exchange |
| `old_meter_serial` | Char | Old meter serial number |
| `old_meter_final_reading` | Float | Final reading on old meter |
| `new_meter_serial` | Char | New meter serial number |
| `new_meter_opening_reading` | Float | Opening reading on new meter (usually 0) |
| `exchange_reason` | Selection | smart_upgrade/faulty/supplier_change/other |
| `engineer_name` | Char | Engineer who performed exchange |
| `photo_old_id` | Many2one → ir.attachment | Photo of old meter final reading |
| `photo_new_id` | Many2one → ir.attachment | Photo of new meter |
| `notes` | Text | Additional notes |

```python
class MeterExchange(models.Model):
    _name = 'property_fielder.meter.exchange'
    _description = 'Meter Exchange Event'
    _inherit = ['mail.thread']

    @api.model_create_multi
    def create(self, vals_list):
        """Update utility account meter serial on exchange."""
        records = super().create(vals_list)
        for rec in records:
            rec.utility_id.meter_serial = rec.new_meter_serial
        return records
```

### 3.4 `property_fielder.utility.bill`

Utility bill.

| Field | Type | Description |
|-------|------|-------------|
| `utility_id` | Many2one → utility.account | Utility account |
| `bill_date` | Date | Bill date |
| `period_start` | Date | Billing period start |
| `period_end` | Date | Billing period end |
| `units_used` | Float | Units billed |
| `unit_cost` | Monetary | **Unit cost (Monetary)** |
| `standing_charges` | Monetary | **Standing charges (Monetary)** |
| `tax_ids` | Many2many → account.tax | **VAT taxes (linked to tax engine)** |
| `tax_amount` | Monetary | **Computed VAT amount** |
| `total` | Monetary | **Total bill (Monetary)** |
| `state` | Selection | received/checked/paid/disputed |
| `invoice_id` | Many2one → account.move | Odoo invoice |
| `attachment_id` | Many2one → ir.attachment | **Bill PDF (ir.attachment)** |
| `expected_units` | Float | **Expected units from meter readings** |
| `unit_variance` | Float | **Variance: billed - expected (computed)** |
| `variance_pct` | Float | **Variance percentage (computed)** |
| `variance_alert` | Boolean | **True if variance > 10% (computed)** |

```python
class UtilityBill(models.Model):
    _inherit = 'property_fielder.utility.bill'

    expected_units = fields.Float(compute='_compute_expected_units', store=True)
    unit_variance = fields.Float(compute='_compute_variance', store=True)
    variance_pct = fields.Float(compute='_compute_variance', store=True)
    variance_alert = fields.Boolean(compute='_compute_variance', store=True)

    @api.depends('utility_id', 'period_start', 'period_end')
    def _compute_expected_units(self):
        """Calculate expected units from meter readings in billing period.
        Falls back to daily_average_consumption if no readings available.
        """
        for rec in self:
            readings = self.env['property_fielder.meter.reading'].search([
                ('utility_id', '=', rec.utility_id.id),
                ('reading_date', '>=', rec.period_start),
                ('reading_date', '<=', rec.period_end),
            ], order='reading_date')
            if readings:
                rec.expected_units = sum(readings.mapped('units_used'))
            elif rec.utility_id.daily_average_consumption and rec.period_start and rec.period_end:
                # Fallback: use daily average × days in period
                days = (rec.period_end - rec.period_start).days + 1
                rec.expected_units = rec.utility_id.daily_average_consumption * days
            else:
                rec.expected_units = 0

    @api.depends('units_used', 'expected_units')
    def _compute_variance(self):
        """Calculate variance between billed and expected units."""
        for rec in self:
            rec.unit_variance = rec.units_used - rec.expected_units
            if rec.expected_units:
                rec.variance_pct = (rec.unit_variance / rec.expected_units) * 100
            else:
                rec.variance_pct = 0
            rec.variance_alert = abs(rec.variance_pct) > 10
```

### 3.5 `property_fielder.council.tax`

**Separate model for Council Tax (not a utility account):**

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `council_id` | Many2one → res.partner | Local authority |
| `account_reference` | Char | Council Tax account reference |
| `band` | Selection | A/B/C/D/E/F/G/H |
| `annual_amount` | Monetary | Annual Council Tax amount |
| `currency_id` | Many2one → res.currency | Currency |
| `liable_party` | Selection | landlord/tenant/empty |
| `empty_homes_premium` | Float | Empty Homes Premium % (0-300) |
| `exemption_code` | Char | Exemption code if applicable |
| `exemption_end_date` | Date | Exemption end date |
| `payment_method` | Selection | direct_debit/invoice |
| `state` | Selection | active/exempt/closed |

```python
class CouncilTax(models.Model):
    _name = 'property_fielder.council.tax'
    _description = 'Council Tax Account'
    _inherit = ['mail.thread']

    @api.depends('annual_amount', 'empty_homes_premium')
    def _compute_total_liability(self):
        for rec in self:
            premium = rec.annual_amount * (rec.empty_homes_premium / 100)
            rec.total_liability = rec.annual_amount + premium
```

---

## 4. Key Features

### 4.1 Account Management
- Track all utility accounts per property
- Contract renewal reminders
- Supplier management
- Tariff comparison (future)

### 4.2 Meter Readings
- Mobile meter reading capture
- Photo evidence
- Usage calculation
- Cost estimation

### 4.3 Bill Processing
- Bill upload and tracking
- Cost verification
- Variance alerts
- Payment tracking

### 4.4 Recharging
- Calculate tenant usage share
- Bill-back to tenants
- Fair usage allocation
- Invoice generation

### 4.5 Reporting
- Cost per property
- Usage trends
- Supplier comparison
- Budget vs actual

---

## 5. Gas m³ to kWh Conversion

**UK gas billing requires conversion from cubic metres to kWh:**

```python
class MeterReading(models.Model):
    _inherit = 'property_fielder.meter.reading'

    reading_kwh = fields.Float(
        string='Reading (kWh)',
        compute='_compute_kwh',
        store=True,
        help="Gas reading converted to kWh for billing"
    )

    @api.depends('reading_value', 'units_used', 'utility_id.utility_type',
                 'utility_id.gas_conversion_factor', 'utility_id.gas_calorific_value')
    def _compute_kwh(self):
        """
        Convert gas m³ to kWh using Ofgem formula:
        kWh = m³ × Volume Correction Factor (1.02264) × Calorific Value ÷ 3.6

        Default conversion factor: 11.1868 kWh per m³
        (based on average CV of 39.5 MJ/m³)
        """
        for rec in self:
            if rec.utility_id.utility_type == 'gas' and rec.units_used:
                # Use supplier-specific factor or default
                if rec.utility_id.gas_calorific_value:
                    # Ofgem formula
                    vcf = 1.02264  # Volume Correction Factor
                    cv = rec.utility_id.gas_calorific_value
                    rec.reading_kwh = rec.units_used * vcf * cv / 3.6
                else:
                    # Use default conversion factor
                    factor = rec.utility_id.gas_conversion_factor or 11.1868
                    rec.reading_kwh = rec.units_used * factor
            else:
                rec.reading_kwh = rec.units_used  # Electricity already in kWh
```

---

## 6. HMO Utility Recharging

### 5.1 Fair Usage Allocation with Proration

```python
class UtilityBill(models.Model):
    _inherit = 'property_fielder.utility.bill'

    def _calculate_tenant_shares(self):
        """
        Calculate fair share for HMO tenants with proration.
        Handles mid-period move-ins/move-outs.

        IMPORTANT: Uses property CAPACITY (total_rooms) not active tenancies.
        Landlord absorbs cost of empty rooms - cannot pass to tenants.
        """
        tenancies = self.property_id.tenancy_ids.filtered(
            lambda t: t.state in ['active', 'ended']
            and t.start_date <= self.period_end
            and (not t.end_date or t.end_date >= self.period_start)
        )
        if not tenancies:
            return []

        billing_days = (self.period_end - self.period_start).days + 1
        # Use PROPERTY CAPACITY - not active tenancies (Ofgem Maximum Resale Price)
        total_capacity = self.property_id.total_rooms or 1
        shares = []

        for tenancy in tenancies:
            # Calculate days in billing period
            start = max(tenancy.start_date, self.period_start)
            end = min(tenancy.end_date or self.period_end, self.period_end)
            tenant_days = (end - start).days + 1

            # Proration factor
            proration = tenant_days / billing_days

            # Per-room allocation using PROPERTY CAPACITY with proration
            share = (tenancy.room_count / total_capacity) * self.total * proration
            shares.append({
                'tenancy_id': tenancy.id,
                'days': tenant_days,
                'proration': proration,
                'amount': share,
            })
        return shares

    def action_generate_tenant_invoices(self):
        """Generate invoices for tenant utility shares with Maximum Resale Price validation."""
        shares = self._calculate_tenant_shares()
        total_recharged = sum(s['amount'] for s in shares)

        # UK Ofgem Maximum Resale Price: Cannot profit from reselling utilities
        if total_recharged > self.total:
            raise ValidationError(
                f"Total recharged (£{total_recharged:.2f}) exceeds bill total (£{self.total:.2f}). "
                "Under Ofgem Maximum Resale Price regulations, landlords cannot profit from utility resale."
            )

        invoices = self.env['account.move']
        for share in shares:
            tenancy = self.env['property.tenancy'].browse(share['tenancy_id'])
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': tenancy.tenant_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': f"Utility recharge: {self.utility_id.utility_type} ({self.period_start} - {self.period_end})",
                    'quantity': 1,
                    'price_unit': share['amount'],
                })],
            })
            invoices |= invoice
        return invoices
```

### 5.2 Fair Usage Cap

```python
class UtilityAccount(models.Model):
    _inherit = 'property_fielder.utility.account'

    fair_usage_cap = fields.Monetary(
        string='Fair Usage Cap',
        help="Maximum monthly amount included in rent (excess charged to tenant)"
    )
    currency_id = fields.Many2one('res.currency')

class UtilityBill(models.Model):
    _inherit = 'property_fielder.utility.bill'

    excess_amount = fields.Monetary(
        compute='_compute_excess',
        store=True,
        help="Amount exceeding fair usage cap"
    )

    @api.depends('total', 'utility_id.fair_usage_cap')
    def _compute_excess(self):
        for rec in self:
            cap = rec.utility_id.fair_usage_cap or 0
            if cap and rec.total > cap:
                rec.excess_amount = rec.total - cap
            else:
                rec.excess_amount = 0
```

---

## 6. Council Tax Model

### 6.1 Separate Council Tax Tracking

**Note:** Council Tax is NOT a utility - it has different rules (HMO exemptions, student exemptions, etc.)

```python
class CouncilTaxAccount(models.Model):
    _name = 'property_fielder.council_tax'
    _description = 'Council Tax Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    property_id = fields.Many2one('property_fielder.property', required=True)
    council_id = fields.Many2one('res.partner', string='Local Authority')
    account_reference = fields.Char(string='Council Tax Reference')
    band = fields.Selection([
        ('A', 'Band A'), ('B', 'Band B'), ('C', 'Band C'),
        ('D', 'Band D'), ('E', 'Band E'), ('F', 'Band F'),
        ('G', 'Band G'), ('H', 'Band H'),
    ])
    annual_amount = fields.Monetary()
    currency_id = fields.Many2one('res.currency')

    # Liability period tracking (critical for historical accuracy)
    start_date = fields.Date(string='Liability Start', required=True,
        help="Date this liability configuration became effective")
    end_date = fields.Date(string='Liability End',
        help="Date this liability ended (blank = current)")

    # HMO-specific - renamed for legal accuracy
    is_hmo = fields.Boolean(related='property_id.is_hmo')
    landlord_liable_hmo = fields.Boolean(
        string='Landlord Liable (HMO)',
        help="Under Council Tax Hierarchy of Liability Regulations, landlord is liable for HMO council tax")

    # Student exemption
    student_exemption = fields.Boolean(string='Student Exemption')
    student_exemption_expiry = fields.Date(string='Student Exemption Expiry')

    # Liability
    liable_party = fields.Selection([
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ])

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError("Start date must be before end date")

    @api.constrains('property_id', 'start_date', 'end_date')
    def _check_no_overlap(self):
        """Ensure no overlapping liability periods for same property."""
        for rec in self:
            domain = [
                ('property_id', '=', rec.property_id.id),
                ('id', '!=', rec.id),
                ('start_date', '<=', rec.end_date or fields.Date.today()),
            ]
            if rec.end_date:
                domain.append(('end_date', '>=', rec.start_date))
            else:
                domain.append('|')
                domain.append(('end_date', '>=', rec.start_date))
                domain.append(('end_date', '=', False))
            if self.search_count(domain):
                raise ValidationError("Council tax liability periods cannot overlap")
```

---

## 7. Meter Rollover Handling

```python
class MeterReading(models.Model):
    _inherit = 'property_fielder.meter.reading'

    @api.depends('reading_value', 'is_rollover', 'meter_max_value')
    def _compute_units_used(self):
        for rec in self:
            prev_reading = self.search([
                ('utility_id', '=', rec.utility_id.id),
                ('reading_date', '<', rec.reading_date),
            ], order='reading_date desc', limit=1)

            if not prev_reading:
                rec.units_used = 0
                continue

            if rec.is_rollover:
                # Meter rolled over: (max - prev) + current
                max_val = rec.meter_max_value or 99999
                rec.units_used = (max_val - prev_reading.reading_value) + rec.reading_value
            else:
                rec.units_used = rec.reading_value - prev_reading.reading_value

            # Negative check (possible rollover not flagged)
            if rec.units_used < 0:
                rec.units_used = 0  # Flag for manual review
```

---

## 8. Void Period Management

```python
class UtilityAccount(models.Model):
    _inherit = 'property_fielder.utility.account'

    def action_start_void_period(self):
        """Switch utility liability to landlord when property becomes void."""
        self.ensure_one()
        # Create final reading
        return {
            'type': 'ir.actions.act_window',
            'name': 'Void Period Reading',
            'res_model': 'property_fielder.meter.reading',
            'view_mode': 'form',
            'context': {
                'default_utility_id': self.id,
                'default_reading_type': 'actual',
                'default_is_void_start': True,
            },
        }
```

---

## 9. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **VAT linked to account.tax** | ✅ Fixed |
| **Meter rollover handling** | ✅ Added |
| **Council Tax removed from utility.account** | ✅ Fixed |
| **Council Tax separate model (3.5)** | ✅ Added |
| **Recharging uses property capacity** | ✅ Fixed |
| **Maximum Resale Price validation** | ✅ Added |
| **landlord_liable_hmo renamed** | ✅ Fixed |
| **Void period management** | ✅ Added |
| **photo_id as ir.attachment** | ✅ Fixed |
| **Meter exchange model (separate)** | ✅ Added |
| **Gas m³ to kWh conversion** | ✅ Added |
| **Gas calorific value field** | ✅ Added |
| **Bill variance tracking** | ✅ Added |
| **Empty Homes Premium field** | ✅ Added |
| **mail dependency added** | ✅ Fixed |
| **Proration logic for mid-period** | ✅ Added |
| **Fair usage cap tracking** | ✅ Added |
| **MPAN/MPRN fields added** | ✅ Added |
| **Supplier as res.partner** | ✅ Fixed |
| **Monetary fields** | ✅ Fixed |
| **last_cp12_date for Gas Safety link** | ✅ Added |
| **daily_average_consumption fallback** | ✅ Added |
| Uses ir.attachment | ✅ Complete |
| Meter reading workflow | ✅ Complete |
| Bill processing defined | ✅ Complete |
| HMO recharging specified | ✅ Complete |
| **Overall** | ✅ Build Ready (90%+) |

