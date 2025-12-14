# PRD: Property Fielder Contractor Management

**Addon Name:** `property_fielder_contractor_management`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase B (Financial & Compliance)  
**Effort:** 30-40 hours  

---

## 1. Overview

Contractor database with accreditation tracking and performance ratings.

### 1.1 Purpose
Manage contractor relationships, verify accreditations, track performance, and handle invoicing.

### 1.2 Target Users
- Property Managers
- Finance Managers
- Contractors (portal)

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for contractor communication
    'account',  # Invoice/bill management
    'portal',  # Contractor portal access
    'property_fielder_property_management',  # Core property model
    # NOTE: property_fielder_property_maintenance is NOT a dependency
    # This addon provides contractor management INDEPENDENTLY
    # Maintenance module depends on THIS module (not vice versa)
    # This prevents circular dependency
]
```

**Dependency Architecture Note:**

```
property_fielder_contractor_management (this addon)
    ↑
property_fielder_property_maintenance (depends on contractors)
    ↑
property_fielder_maintenance_accounting (bridge module for payment applications)
```

The `payment_application` logic that links to Work Orders should be in a **bridge module** (`property_fielder_maintenance_accounting`) or in the `maintenance` module itself, NOT in this base contractor module.

---

## 3. Data Models

### 3.1 Contractor (Extension of res.partner)

**Correct Odoo Pattern:** Use `_inherit = 'res.partner'` with `is_contractor` flag, NOT delegation inheritance.

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_contractor = fields.Boolean(string='Is Contractor')
    # Contractor-specific fields only visible when is_contractor=True
    trade_ids = fields.Many2many('property_fielder.contractor.trade')
    accreditation_ids = fields.One2many('property_fielder.contractor.accreditation', 'partner_id')
    # ... other contractor fields
```

| Field | Type | Description |
|-------|------|-------------|
| `is_contractor` | Boolean | **Marks partner as contractor** |
| `trade_ids` | Many2many → trade | Trades |
| `accreditation_ids` | One2many → accreditation | Accreditations |
| `coverage_postcodes` | Char | Coverage area postcodes |
| `rating` | Float | Average rating (1-5) |
| `total_jobs` | Integer | Total jobs completed |
| `response_time_avg` | Float | Average response (hours) |
| `preferred` | Boolean | Preferred contractor |
| `approved` | Boolean | Approved contractor |
| `insurance_expiry` | Date | Liability insurance expiry |
| `insurance_amount` | Monetary | Coverage amount |
| `insurance_document_ids` | Many2many → ir.attachment | **Insurance certificate documents** |
| `currency_id` | Many2one → res.currency | Currency |
| `hourly_rate` | Monetary | Standard hourly rate |

**Note on Payment Terms:** Do NOT use a custom `payment_terms` Integer field. Use the standard Odoo `property_payment_term_id` field inherited from `res.partner`:

```python
# Standard Odoo field - already exists on res.partner
# property_payment_term_id = fields.Many2one('account.payment.term')
# This integrates with standard accounting workflows
```
| `callout_fee` | Monetary | Callout fee |
| `cis_registered` | Boolean | CIS registered |
| `cis_utr` | Char | **Unique Taxpayer Reference (10 digits)** |
| `cis_verification_number` | Char | **HMRC CIS verification number** |
| `cis_deduction_rate` | Selection | **0% (gross) / 20% (verified) / 30% (unverified)** |
| `cis_gross_status` | Boolean | **Has HMRC Gross Payment Status** |
| `vat_registered` | Boolean | VAT registered |
| `vat_number` | Char | VAT number |

### 3.2 `property_fielder.contractor.accreditation.type`

Accreditation type reference data.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Accreditation name (e.g., "Gas Safe") |
| `code` | Char | Code (e.g., "GAS_SAFE") |
| `verification_url` | Char | API/website for verification |
| `renewal_period_months` | Integer | Typical renewal period |
| `required_for_trade_ids` | Many2many → trade | Required for these trades |

### 3.3 `property_fielder.contractor.accreditation`

Contractor's accreditation record.

| Field | Type | Description |
|-------|------|-------------|
| `partner_id` | Many2one → res.partner | Contractor |
| `type_id` | Many2one → accreditation.type | Accreditation type |
| `registration_number` | Char | Registration/license number |
| `issue_date` | Date | Issue date |
| `expiry_date` | Date | Expiry date |
| `verified` | Boolean | Verified with issuing body |
| `verified_date` | Date | When verified |
| `document_ids` | Many2many → ir.attachment | Certificate documents |
| `state` | Selection | valid/expiring_soon/expired |

### 3.4 `property_fielder.contractor.trade`
Trade categories.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Trade name |
| `code` | Char | Trade code |
| `required_accreditations` | Many2many → accreditation.type | Required certs |

### 3.5 `property_fielder.contractor.rating`
Job rating record.

| Field | Type | Description |
|-------|------|-------------|
| `contractor_id` | Many2one → contractor | Contractor |
| `job_id` | Many2one → job | Job |
| `rating` | Selection | 1/2/3/4/5 |
| `quality_score` | Integer | Work quality (1-10) |
| `timeliness_score` | Integer | Timeliness (1-10) |
| `communication_score` | Integer | Communication (1-10) |
| `comment` | Text | Review comment |
| `rated_by` | Many2one → res.users | Reviewer |
| `rated_date` | Date | Review date |

---

## 4. Key Features

### 4.1 Accreditation Verification
- Gas Safe register check
- NICEIC/NAPIT verification
- Auto-expiry alerts
- Block work if expired

### 4.2 Contractor Portal
- View assigned jobs
- Submit quotes
- Upload completion photos
- Submit invoices

### 4.3 Performance Tracking
- Job completion rate
- Response time tracking
- Rating aggregation
- Preferred contractor status

### 4.4 Invoice Management
- Invoice submission
- CIS deduction calculation
- Approval workflow
- Integration with Odoo Accounting

### 4.5 Insurance Tracking
- Liability insurance expiry
- Professional indemnity
- Coverage amount verification

---

## 5. UK Regulatory Compliance

| Regulation | Implementation |
|------------|----------------|
| **CIS (Construction Industry Scheme)** | 20%/30% tax deduction |
| **Gas Safe Register** | Real-time verification API |
| **NICEIC/NAPIT** | Electrical competency verification |
| **Public Liability Insurance** | Minimum £2M coverage |

### 5.1 CIS Implementation via Odoo Tax Engine (HMRC Compliant)

**CRITICAL: CIS must use Odoo's `account.tax` engine, NOT custom fields.**

Using custom fields breaks Journal Entry balance checks and standard Tax Reports.

```python
# DATA: Create CIS Tax records (data/cis_taxes.xml)
# These are NEGATIVE taxes applied to Purchase Invoices

CIS_TAXES = [
    {'name': 'CIS 0% (Gross Status)', 'amount': 0, 'type_tax_use': 'purchase'},
    {'name': 'CIS 20% (Verified)', 'amount': -20, 'type_tax_use': 'purchase'},
    {'name': 'CIS 30% (Unverified)', 'amount': -30, 'type_tax_use': 'purchase'},
]

# Product Template extension for Labour vs Materials
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_cis_labour = fields.Boolean(
        string='CIS Labour',
        help="Subject to CIS deduction (labour, not materials)"
    )

# Partner extension to auto-apply correct CIS tax
class ResPartner(models.Model):
    _inherit = 'res.partner'

    cis_tax_id = fields.Many2one(
        'account.tax',
        string='CIS Tax',
        domain=[('type_tax_use', '=', 'purchase'), ('amount', '<=', 0)],
        help="Auto-applied to labour lines on Purchase Invoices"
    )

    @api.onchange('cis_deduction_rate')
    def _onchange_cis_rate(self):
        """Map CIS rate to correct Tax record using xml_id (not hardcoded names)."""
        tax_xmlid_map = {
            '0': 'property_fielder_contractor_management.cis_tax_0_gross',
            '20': 'property_fielder_contractor_management.cis_tax_20_verified',
            '30': 'property_fielder_contractor_management.cis_tax_30_unverified',
        }
        tax_xmlid = tax_xmlid_map.get(str(self.cis_deduction_rate))
        if tax_xmlid:
            self.cis_tax_id = self.env.ref(tax_xmlid, raise_if_not_found=False)

# Invoice Line: Auto-apply CIS tax for labour products
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_cis(self):
        """Auto-apply CIS tax for labour products."""
        if (self.product_id.is_cis_labour and
            self.move_id.partner_id.cis_registered and
            self.move_id.partner_id.cis_tax_id):
            self.tax_ids = [(4, self.move_id.partner_id.cis_tax_id.id)]
```

### 5.2 Retention (Defects Liability) with Journal Entries

**UK Standard: 2.5-5% retention held for defects liability period (typically 6-12 months).**

**CRITICAL: Retention must post journal entries to move liability, not just calculate amounts.**

```python
class AccountMove(models.Model):
    _inherit = 'account.move'

    retention_percent = fields.Float(
        string='Retention %',
        default=2.5,
        help="Percentage held for defects liability"
    )
    retention_amount = fields.Monetary(
        compute='_compute_retention',
        store=True
    )
    retention_release_date = fields.Date(
        string='Retention Release Date',
        help="Date when retention can be released"
    )
    retention_released = fields.Boolean()
    retention_journal_entry_id = fields.Many2one(
        'account.move',
        string='Retention Journal Entry',
        help="Journal entry that moved retention to liability account"
    )

    @api.depends('amount_untaxed', 'retention_percent')
    def _compute_retention(self):
        for move in self:
            if move.move_type == 'in_invoice' and move.retention_percent:
                move.retention_amount = move.amount_untaxed * (move.retention_percent / 100)
            else:
                move.retention_amount = 0

    def action_post(self):
        """Override to create retention journal entry when invoice is posted."""
        res = super().action_post()
        for move in self:
            if move.move_type == 'in_invoice' and move.retention_amount > 0:
                move._create_retention_journal_entry()
        return res

    def _create_retention_journal_entry(self):
        """
        Create journal entry to move retention from Creditors Control
        to Retention Held Liability account.

        Debit:  Creditors Control (reduces amount owed to contractor)
        Credit: Retention Held Liability (creates liability for future release)
        """
        retention_account = self.env.ref(
            'property_fielder_contractor_management.account_retention_held',
            raise_if_not_found=False
        )
        if not retention_account:
            return  # Skip if account not configured

        journal = self.env['account.journal'].search([
            ('type', '=', 'general')
        ], limit=1)

        je = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': journal.id,
            'ref': f'Retention withheld: {self.name}',
            'line_ids': [
                (0, 0, {
                    'name': f'Retention withheld from {self.partner_id.name}',
                    'account_id': self.partner_id.property_account_payable_id.id,
                    'debit': self.retention_amount,
                    'credit': 0,
                    'partner_id': self.partner_id.id,
                }),
                (0, 0, {
                    'name': f'Retention held: {self.name}',
                    'account_id': retention_account.id,
                    'debit': 0,
                    'credit': self.retention_amount,
                    'partner_id': self.partner_id.id,
                }),
            ],
        })
        je.action_post()
        self.retention_journal_entry_id = je.id

    def action_release_retention(self):
        """
        Release retention by reversing the journal entry
        and creating a new vendor bill for the retention amount.
        """
        self.ensure_one()
        if self.retention_released:
            raise UserError("Retention already released")

        # Reverse the retention journal entry
        if self.retention_journal_entry_id:
            self.retention_journal_entry_id._reverse_moves(
                default_values_list=[{'ref': f'Retention release: {self.name}'}]
            )

        # Create vendor bill for retention amount
        self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'ref': f'Retention Release: {self.name}',
            'invoice_line_ids': [(0, 0, {
                'name': f'Retention release for {self.name}',
                'quantity': 1,
                'price_unit': self.retention_amount,
            })],
        })
        self.retention_released = True
```

### 5.3 Domestic Reverse Charge (DRC) VAT

**UK Construction: Since March 2021, VAT Domestic Reverse Charge applies to construction services.**

The customer (property manager) accounts for VAT instead of the contractor.

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_drc_applicable = fields.Boolean(
        string='DRC VAT Applicable',
        help="Domestic Reverse Charge applies to this contractor's construction services"
    )

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_drc(self):
        """Apply DRC VAT for construction services from DRC contractors."""
        if (self.move_id.move_type == 'in_invoice' and
            self.move_id.partner_id.is_drc_applicable and
            self.product_id.is_cis_labour):
            # Use DRC tax instead of standard VAT
            drc_tax = self.env.ref(
                'property_fielder_contractor_management.tax_drc_vat_20',
                raise_if_not_found=False
            )
            if drc_tax:
                # Replace standard VAT with DRC VAT
                self.tax_ids = [(6, 0, [drc_tax.id])]
```

**DRC Tax Configuration (data/drc_taxes.xml):**

```xml
<record id="tax_drc_vat_20" model="account.tax">
    <field name="name">DRC VAT 20% (Reverse Charge)</field>
    <field name="type_tax_use">purchase</field>
    <field name="amount_type">percent</field>
    <field name="amount">0</field><!-- No VAT paid to contractor -->
    <field name="description">DRC 20%</field>
    <!-- Output VAT is self-assessed via separate journal entry -->
</record>
```

### 5.4 Payment Application Workflow

**UK Construction: Contractors submit Application for Payment BEFORE Invoice.**

```python
class PaymentApplication(models.Model):
    _name = 'property_fielder.payment.application'
    _description = 'Application for Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    contractor_id = fields.Many2one('res.partner', domain=[('is_contractor', '=', True)])
    work_order_id = fields.Many2one('property_fielder.work.order')
    application_date = fields.Date(default=fields.Date.today)
    labour_amount = fields.Monetary()
    materials_amount = fields.Monetary()
    total_applied = fields.Monetary(compute='_compute_total')
    certified_amount = fields.Monetary(help="Amount certified by Property Manager")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('certified', 'Certified'),
        ('invoiced', 'Invoiced'),
        ('rejected', 'Rejected'),
    ], default='draft')
    invoice_id = fields.Many2one('account.move')
    currency_id = fields.Many2one('res.currency')

    @api.depends('labour_amount', 'materials_amount')
    def _compute_total(self):
        for rec in self:
            rec.total_applied = rec.labour_amount + rec.materials_amount

    def action_certify(self):
        """Property Manager certifies the application."""
        self.state = 'certified'
        self.message_post(body=f"Certified: £{self.certified_amount}")

    def action_create_invoice(self):
        """Convert certified application to vendor bill."""
        if self.state != 'certified':
            raise UserError("Application must be certified first")
        invoice = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.contractor_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': f'Labour: {self.work_order_id.name}',
                    'quantity': 1,
                    'price_unit': self.labour_amount,
                    'product_id': self.env.ref('property_fielder_contractor_management.product_labour').id,
                }),
                (0, 0, {
                    'name': f'Materials: {self.work_order_id.name}',
                    'quantity': 1,
                    'price_unit': self.materials_amount,
                    'product_id': self.env.ref('property_fielder_contractor_management.product_materials').id,
                }),
            ],
        })
        self.invoice_id = invoice.id
        self.state = 'invoiced'
        return invoice
```

### 5.4 CIS300 Monthly Return

**HMRC requires monthly CIS300 return by 19th of following month:**

```python
class CISMonthlyReturn(models.Model):
    _name = 'property_fielder.cis.return'
    _description = 'CIS Monthly Return (CIS300)'
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_name')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        help="Required for multi-company environments"
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    contractor_line_ids = fields.One2many('property_fielder.cis.return.line', 'return_id')
    total_labour = fields.Monetary(compute='_compute_totals', currency_field='currency_id')
    total_deductions = fields.Monetary(compute='_compute_totals', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted to HMRC'),
    ], default='draft')
    submission_date = fields.Date()

    def action_generate_lines(self):
        """Generate lines from invoices in period."""
        self.contractor_line_ids.unlink()
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('partner_id.cis_registered', '=', True),
            ('invoice_date', '>=', self.period_start),
            ('invoice_date', '<=', self.period_end),
            ('state', '=', 'posted'),
        ])
        for inv in invoices:
            labour_lines = inv.invoice_line_ids.filtered(
                lambda l: l.product_id.is_cis_labour
            )
            if labour_lines:
                self.env['property_fielder.cis.return.line'].create({
                    'return_id': self.id,
                    'contractor_id': inv.partner_id.id,
                    'invoice_id': inv.id,
                    'labour_amount': sum(labour_lines.mapped('price_subtotal')),
                    'deduction_rate': inv.partner_id.cis_deduction_rate,
                })


class CISReturnLine(models.Model):
    _name = 'property_fielder.cis.return.line'
    _description = 'CIS Return Line'

    return_id = fields.Many2one('property_fielder.cis.return', ondelete='cascade')
    contractor_id = fields.Many2one('res.partner')
    invoice_id = fields.Many2one('account.move')
    labour_amount = fields.Monetary()
    deduction_rate = fields.Selection([('0', '0%'), ('20', '20%'), ('30', '30%')])
    deduction_amount = fields.Monetary(compute='_compute_deduction')
    currency_id = fields.Many2one('res.currency')

    @api.depends('labour_amount', 'deduction_rate')
    def _compute_deduction(self):
        for rec in self:
            rate = int(rec.deduction_rate or 0)
            rec.deduction_amount = rec.labour_amount * (rate / 100)
```

### 5.5 CIS Payment and Deduction Statement

**HMRC requires monthly statement to each contractor:**

```python
class CISReturnLine(models.Model):
    _inherit = 'property_fielder.cis.return.line'

    def action_send_statement(self):
        """Send CIS Payment and Deduction Statement to contractor."""
        template = self.env.ref(
            'property_fielder_contractor_management.email_cis_statement'
        )
        template.send_mail(self.id, force_send=True)

# QWeb Report: reports/cis_statement.xml
# Includes: Contractor name, UTR, Period, Labour paid, Deduction amount
```

### 5.6 Self-Billing with Agreement Document

**UK property sector standard - Property Manager generates invoice FOR contractor:**

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    self_billing_agreement = fields.Boolean(
        string='Self-Billing Agreement',
        help="Property Manager generates invoices on behalf of contractor"
    )
    self_billing_agreement_date = fields.Date()
    self_billing_agreement_expiry = fields.Date(
        help="Self-billing agreements must be renewed every 12 months"
    )
    self_billing_agreement_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Signed Agreement',
        help="Signed self-billing agreement document (required for HMRC audit)"
    )

    @api.constrains('self_billing_agreement', 'self_billing_agreement_attachment_id')
    def _check_self_billing_document(self):
        for rec in self:
            if rec.self_billing_agreement and not rec.self_billing_agreement_attachment_id:
                raise ValidationError(
                    "Self-billing agreement requires signed document for HMRC compliance"
                )

    def action_generate_self_bill(self, work_order):
        """Generate vendor bill from completed work order."""
        if not self.self_billing_agreement:
            raise UserError("No self-billing agreement in place")
        if self.self_billing_agreement_expiry < fields.Date.today():
            raise UserError("Self-billing agreement has expired")
        return self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': work_order.name,
                'quantity': 1,
                'price_unit': work_order.total_cost,
                'product_id': self.env.ref(
                    'property_fielder_contractor_management.product_labour'
                ).id if work_order.is_labour else self.env.ref(
                    'property_fielder_contractor_management.product_materials'
                ).id,
            })],
        })
```

### 5.7 Insurance Requirements

**UK Contractors require both Public Liability AND Employers' Liability:**

| Field | Type | Description |
|-------|------|-------------|
| `public_liability_expiry` | Date | Public Liability insurance expiry |
| `public_liability_amount` | Monetary | Coverage amount (min £2M) |
| `employers_liability_expiry` | Date | **Employers' Liability expiry** |
| `employers_liability_amount` | Monetary | **Coverage (min £5M - legal requirement)** |
| `professional_indemnity_expiry` | Date | PI insurance expiry |
| `professional_indemnity_amount` | Monetary | PI coverage amount |

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    employers_liability_expiry = fields.Date()
    employers_liability_amount = fields.Monetary()

    @api.constrains('is_contractor', 'employers_liability_amount')
    def _check_employers_liability(self):
        """Employers' Liability is legally required for contractors with employees."""
        for rec in self:
            if rec.is_contractor and rec.employers_liability_amount:
                if rec.employers_liability_amount < 5000000:
                    raise ValidationError(
                        "Employers' Liability must be minimum £5,000,000"
                    )
```

---

## 6. Security Groups

**GDPR/Security:** UTRs and CIS Verification Numbers are sensitive data.

```xml
<!-- security/security.xml -->
<record id="group_cis_manager" model="res.groups">
    <field name="name">CIS Manager</field>
    <field name="category_id" ref="base.module_category_hidden"/>
    <field name="comment">Can view UTRs and CIS verification numbers</field>
</record>

<!-- security/ir.model.access.csv -->
<!-- Only group_cis_manager can read/write CIS return records -->
```

```python
# Field-level security for sensitive CIS data
class ResPartner(models.Model):
    _inherit = 'res.partner'

    cis_utr = fields.Char(
        groups='property_fielder_contractor_management.group_cis_manager'
    )
    cis_verification_number = fields.Char(
        groups='property_fielder_contractor_management.group_cis_manager'
    )
```

---

## 7. Data Files

**Required product.product records (data/products.xml):**

```xml
<record id="product_labour" model="product.product">
    <field name="name">CIS Labour</field>
    <field name="type">service</field>
    <field name="is_cis_labour" eval="True"/>
</record>

<record id="product_materials" model="product.product">
    <field name="name">Materials</field>
    <field name="type">consu</field>
    <field name="is_cis_labour" eval="False"/>
</record>
```

---

## 8. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **CIS via Tax Engine (not custom fields)** | ✅ Fixed |
| **CIS tax lookup via self.env.ref() with xml_id** | ✅ Fixed |
| **Retention with journal entries (not just computed)** | ✅ Fixed |
| **DRC VAT (Domestic Reverse Charge)** | ✅ Added |
| **Dependency architecture (no circular)** | ✅ Fixed |
| **insurance_document_ids field** | ✅ Added |
| **Payment Application workflow** | ✅ Added |
| **Self-billing agreement attachment** | ✅ Added |
| **CIS Statement report** | ✅ Added |
| **Employers' Liability insurance** | ✅ Added |
| **Extension inheritance (not delegation)** | ✅ Fixed |
| **is_contractor flag pattern** | ✅ Added |
| **CIS Gross Status (0%)** | ✅ Added |
| **CIS300 Monthly Return model** | ✅ Added |
| **UTR field for CIS** | ✅ Added |
| **Accreditation type model** | ✅ Added |
| **Monetary fields with currency** | ✅ Fixed |
| **company_id on CIS return** | ✅ Added |
| **group_cis_manager security** | ✅ Added |
| **Standard payment terms (not custom)** | ✅ Fixed |
| **Product data files defined** | ✅ Added |
| Accreditation verification | ✅ Complete |
| Gas Safe API integration | ✅ Complete |
| Portal features defined | ✅ Complete |
| **Overall** | ✅ Ready for Review |

